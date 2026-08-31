import json

REQUIRED_FIELDS = [
    "zone",
    "forecast_time",
    "precipitation_forecast_mm",
    "ratio_projected",
    "risk",
    "current_earnings",
    "earnings_recommended",
]

def load_alert(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        alert = json.load(f)

    missing = [x for x in REQUIRED_FIELDS if x not in alert]
    if missing:
        raise ValueError(f"Missing alert fields: {missing}")

    # Guardrail: the LLM cannot override the analytical recommendation.
    if alert["earnings_recommended"] < alert["current_earnings"]:
        raise ValueError(
            "Recommended earnings cannot be below current earnings."
        )

    return alert
