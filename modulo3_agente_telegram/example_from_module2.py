"""
Ejemplo de integración conceptual:

alerts = run_alert_engine(forecast)

for _, row in alerts.iterrows():
    alert = {
        "zone": row["ZONE"],
        "forecast_time": str(row["FORECAST_TIME"]),
        "precipitation_forecast_mm": float(row["PRECIPITATION_FORECAST_MM"]),
        "ratio_projected": float(row["RATIO_PROJECTED"]),
        "risk": row["RISK"],
        "current_earnings": float(row["CURRENT_EARNINGS"]),
        "earnings_recommended": float(row["earnings_recommended"]),
        "increment_mxn": float(row["increment_mxn"]),
        "increment_pct": float(row["increment_pct"]),
        "action_window_minutes": 30,
        "secondary_zones": [],
        "historical_basis": "Hallazgos del Módulo 1"
    }

    # Guardar cada alerta como JSON y pasarla a agent.py.
"""
