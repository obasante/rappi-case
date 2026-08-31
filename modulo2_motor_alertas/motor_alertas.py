import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import statsmodels.formula.api as smf
from shapely import wkt
from shapely.geometry import Point

TARGET_RATIO = 1.8
RAIN_THRESHOLD = 1.0
COOLDOWN_MINUTES = 120
LOOKAHEAD_HOURS = 2
TIMEZONE = "America/Monterrey"


def load_data(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el Excel: {path}")
    df = pd.read_excel(path, sheet_name="RAW_DATA")
    zone_info = pd.read_excel(path, sheet_name="ZONE_INFO")
    zone_polygons = pd.read_excel(path, sheet_name="ZONE_POLYGONS")
    df["DATE"] = pd.to_datetime(df["DATE"])
    df["RATIO"] = df["ORDERS"] / df["CONNECTED_RT"]
    df["SATURATION"] = df["RATIO"] > TARGET_RATIO
    return df, zone_info, zone_polygons


def prepare_zones(zone_info, zone_polygons):
    centers = zone_info.set_index("ZONE")[["LATITUDE_CENTER", "LONGITUDE_CENTER"]].to_dict("index")
    rows, geometries = [], {}
    for _, r in zone_polygons.iterrows():
        zone = r["ZONE_NAME"]
        try:
            geom = wkt.loads(r["GEOMETRY_WKT"])
            method = "polygon"
            if not geom.is_valid:
                geom = geom.buffer(0)
                method = "polygon_repaired"
            p = geom.representative_point()
            lat, lon = p.y, p.x
            geometries[zone] = geom
        except Exception:
            if zone not in centers:
                raise ValueError(f"No hay coordenadas para {zone}")
            lat = centers[zone]["LATITUDE_CENTER"]
            lon = centers[zone]["LONGITUDE_CENTER"]
            method = "fallback_center"
            geometries[zone] = None
        rows.append({"ZONE": zone, "LAT_QUERY": float(lat), "LON_QUERY": float(lon), "MAPPING_METHOD": method})
    zones = pd.DataFrame(rows)
    if zones["ZONE"].nunique() != 14:
        raise ValueError(f"Se esperaban 14 zonas; se encontraron {zones['ZONE'].nunique()}.")
    return zones, geometries


def point_in_polygon(lat, lon, geometries):
    p = Point(float(lon), float(lat))
    for zone, geom in geometries.items():
        if geom is not None and (geom.contains(p) or geom.covers(p)):
            return zone
    return None


def get_forecast(zones):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ",".join(zones["LAT_QUERY"].round(6).astype(str)),
        "longitude": ",".join(zones["LON_QUERY"].round(6).astype(str)),
        "hourly": "precipitation",
        "forecast_days": 2,
        "timezone": TIMEZONE,
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as e:
        raise RuntimeError("Open-Meteo no respondió. El motor no genera alertas con forecast incompleto.") from e
    if not isinstance(payload, list):
        payload = [payload]
    if len(payload) != len(zones):
        raise RuntimeError("La respuesta de Open-Meteo no coincide con las 14 zonas consultadas.")
    rows = []
    for i, item in enumerate(payload):
        z = zones.iloc[i]
        for t, rain in zip(item["hourly"]["time"], item["hourly"]["precipitation"]):
            rows.append({
                "ZONE_QUERY": z["ZONE"], "FORECAST_TIME": pd.to_datetime(t),
                "PRECIPITATION_FORECAST_MM": float(rain or 0),
                "MAPPING_METHOD": z["MAPPING_METHOD"],
                "API_LATITUDE": item.get("latitude"), "API_LONGITUDE": item.get("longitude")
            })
    return pd.DataFrame(rows)


def fit_models(df):
    ratio_model = smf.ols("RATIO ~ PRECIPITATION_MM + C(HOUR) + C(ZONE)", data=df).fit()
    earnings_model = smf.ols("RATIO ~ EARNINGS + PRECIPITATION_MM + C(HOUR) + C(ZONE)", data=df).fit()
    beta = earnings_model.params["EARNINGS"]
    if beta >= 0:
        raise ValueError("El coeficiente de EARNINGS no es negativo; no se puede despejar un incentivo mayor.")
    return ratio_model, earnings_model, beta


def project_ratio(model, zone, hour, rain):
    x = pd.DataFrame({"PRECIPITATION_MM": [rain], "HOUR": [int(hour)], "ZONE": [zone]})
    return float(model.predict(x).iloc[0])


def recommended_earnings(model, beta, zone, hour, rain, current):
    x0 = pd.DataFrame({"EARNINGS": [0], "PRECIPITATION_MM": [rain], "HOUR": [int(hour)], "ZONE": [zone]})
    intercept = float(model.predict(x0).iloc[0])
    required = (TARGET_RATIO - intercept) / beta
    recommended = int(np.ceil(max(float(current), required)))
    inc = recommended - float(current)
    return recommended, inc, (inc / float(current) * 100 if float(current) > 0 else np.nan)


def risk(ratio):
    if ratio > 1.8: return "CRÍTICO"
    if ratio >= 1.5: return "ALTO"
    if ratio >= 1.2: return "MEDIO"
    return "BAJO"


def event_id(zone, timestamp):
    t = pd.Timestamp(timestamp)
    block = t.floor("h") - pd.Timedelta(minutes=t.minute % COOLDOWN_MINUTES)
    return f"{zone}_{block:%Y%m%d_%H%M}"


def run_engine(df, forecast, geometries):
    ratio_model, earnings_model, beta = fit_models(df)
    forecast = forecast.copy()
    forecast["ZONE_MAPPED"] = forecast.apply(lambda r: point_in_polygon(r["API_LATITUDE"], r["API_LONGITUDE"], geometries), axis=1)
    forecast["ZONE"] = forecast["ZONE_MAPPED"].fillna(forecast["ZONE_QUERY"])
    forecast = forecast.sort_values(["ZONE", "FORECAST_TIME"])
    start = forecast["FORECAST_TIME"].min()
    end = start + pd.Timedelta(hours=LOOKAHEAD_HOURS - 1)
    window = forecast[(forecast["FORECAST_TIME"] >= start) & (forecast["FORECAST_TIME"] <= end)].copy()
    idx = window.groupby("ZONE")["PRECIPITATION_FORECAST_MM"].idxmax()
    data = window.loc[idx].copy()
    data["HOUR"] = data["FORECAST_TIME"].dt.hour
    data["RATIO_PROJECTED"] = data.apply(lambda r: project_ratio(ratio_model, r["ZONE"], r["HOUR"], r["PRECIPITATION_FORECAST_MM"]), axis=1)
    data["RISK"] = data["RATIO_PROJECTED"].apply(risk)
    latest = df.sort_values(["ZONE", "DATE", "HOUR"]).groupby("ZONE").tail(1).set_index("ZONE")["EARNINGS"].to_dict()
    data["CURRENT_EARNINGS"] = data["ZONE"].map(latest)
    data["TRIGGER"] = (data["RATIO_PROJECTED"] > TARGET_RATIO) | ((data["PRECIPITATION_FORECAST_MM"] > RAIN_THRESHOLD) & (data["RATIO_PROJECTED"] >= 1.5))
    alerts = data[data["TRIGGER"]].copy()
    if alerts.empty:
        return alerts
    rec = alerts.apply(lambda r: recommended_earnings(earnings_model, beta, r["ZONE"], r["HOUR"], r["PRECIPITATION_FORECAST_MM"], r["CURRENT_EARNINGS"]), axis=1, result_type="expand")
    rec.columns = ["EARNINGS_RECOMMENDED", "INCREMENT_MXN", "INCREMENT_PCT"]
    alerts = pd.concat([alerts.reset_index(drop=True), rec], axis=1)
    alerts["EVENT_ID"] = alerts.apply(lambda r: event_id(r["ZONE"], r["FORECAST_TIME"]), axis=1)
    return alerts.drop_duplicates("EVENT_ID").sort_values("RATIO_PROJECTED", ascending=False)


def save_alert(alerts, output):
    if alerts.empty:
        return None
    order = {"CRÍTICO": 4, "ALTO": 3, "MEDIO": 2, "BAJO": 1}
    a = alerts.copy(); a["SEVERITY"] = a["RISK"].map(order); a = a.sort_values(["SEVERITY", "RATIO_PROJECTED"], ascending=[False, False])
    p = a.iloc[0]
    secondary = [z for z in a["ZONE"].tolist() if z != p["ZONE"]][:2]
    result = {
        "zone": str(p["ZONE"]), "forecast_time": pd.Timestamp(p["FORECAST_TIME"]).strftime("%H:%M"),
        "precipitation_forecast_mm": round(float(p["PRECIPITATION_FORECAST_MM"]), 2),
        "ratio_projected": round(float(p["RATIO_PROJECTED"]), 2), "risk": str(p["RISK"]),
        "current_earnings": round(float(p["CURRENT_EARNINGS"]), 2), "earnings_recommended": int(p["EARNINGS_RECOMMENDED"]),
        "increment_mxn": round(float(p["INCREMENT_MXN"]), 2), "increment_pct": round(float(p["INCREMENT_PCT"]), 1),
        "action_window_minutes": 30, "secondary_zones": secondary,
        "historical_basis": "El ratio histórico aumenta bajo mayores niveles de precipitación y el motor controla por hora y zona."
    }
    Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def demo(df, output):
    ratio_model, earnings_model, beta = fit_models(df)
    ratio = project_ratio(ratio_model, "Santiago", 14, 7.2)
    rec, inc, pct = recommended_earnings(earnings_model, beta, "Santiago", 14, 7.2, 55)
    result = {"zone":"Santiago","forecast_time":"14:00","precipitation_forecast_mm":7.2,"ratio_projected":round(ratio,2),"risk":risk(ratio),"current_earnings":55,"earnings_recommended":rec,"increment_mxn":inc,"increment_pct":round(pct,1),"action_window_minutes":30,"secondary_zones":["Carretera Nacional","Santa Catarina"],"historical_basis":"El análisis histórico muestra mayor sensibilidad operacional bajo condiciones de lluvia."}
    Path(output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="../rappi_delivery_case_data.xlsx")
    parser.add_argument("--output", default="alert_for_agent.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    df, zone_info, zone_polygons = load_data(args.input)
    if args.demo:
        demo(df, args.output); return
    zones, geometries = prepare_zones(zone_info, zone_polygons)
    print(f"Zonas cargadas: {zones['ZONE'].nunique()}")
    print("Consultando Open-Meteo...")
    forecast = get_forecast(zones)
    print(f"Forecast recibido: {len(forecast):,} filas")
    alerts = run_engine(df, forecast, geometries)
    if alerts.empty:
        print("No se detectó una condición que active una alerta.")
        return
    print(f"Alertas generadas: {len(alerts)}")
    print(alerts[["ZONE","FORECAST_TIME","PRECIPITATION_FORECAST_MM","RATIO_PROJECTED","RISK","CURRENT_EARNINGS","EARNINGS_RECOMMENDED"]].round(2).to_string(index=False))
    if args.dry_run:
        print("[DRY RUN] No se generó JSON para el agente.")
        return
    result = save_alert(alerts, args.output)
    print("\n===== ALERTA ESTRUCTURADA =====")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nArchivo creado: {args.output}")


if __name__ == "__main__":
    main()
