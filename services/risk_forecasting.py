"""
services/risk_forecasting.py

Predictive Compliance & Risk Forecasting for RegScale CCM

This module implements a simple forecasting service that predicts future control failure risk scores
based on historical audit data. It corresponds to the "Predictive Compliance & Risk Forecasting"
feature in `docs/FEATURE_PROPOSALS.md`.

Key functions:
- `fetch_historical_risk(control_id, days)`: Mock retrieval of historical daily risk scores.
- `simple_moving_average(values, window)`: Compute moving average as a baseline forecasting method.
- `forecast_risk(control_id, days, forecast_horizon)`: Generate future risk score predictions.
- `simulate_policy_change(control_id, baseline_days, horizon, adjustment_function)`: "What-If" simulation
  showing impact of policy changes on future risk.

Why this approach?
- **Proactive Remediation:** Identifies controls likely to fail, prioritizing resources.
- **Cost-Effective:** Uses lightweight statistical methods (no heavy ML infra required).
- **Extendable:** Swap in ARIMA, Prophet, or a trained ML model for more accuracy.

Usage:
    from services.risk_forecasting import forecast_risk, simulate_policy_change
    preds = forecast_risk('AC-2', days=30, forecast_horizon=7)
    sim = simulate_policy_change(
        control_id='AC-2', baseline_days=30, horizon=7,
        adjustment_function=lambda x: x * 0.9  # simulate 10% improvement
    )
    print('Forecast:', preds)
    print('Simulation:', sim)
"""

import datetime
import random
from typing import List, Tuple, Callable


def fetch_historical_risk(control_id: str, days: int = 30) -> List[Tuple[datetime.date, float]]:
    """
    Mock function to fetch historical daily risk scores for a control.
    Risk scores range 0.0 (no risk) to 1.0 (high risk).

    Args:
        control_id: Identifier of the control (e.g., 'AC-2').
        days: Number of past days to retrieve.

    Returns:
        List of (date, risk_score) tuples.
    """
    today = datetime.date.today()
    data = []
    for i in range(days, 0, -1):
        date = today - datetime.timedelta(days=i)
        # Simulate risk with random walk
        base = 0.3 if control_id.endswith('1') else 0.5
        noise = random.uniform(-0.05, 0.05)
        score = min(max(base + noise, 0.0), 1.0)
        data.append((date, score))
    return data


def simple_moving_average(values: List[float], window: int = 7) -> List[float]:
    """
    Compute simple moving average forecast for the next point.

    Args:
        values: List of historical risk scores.
        window: Number of points to average.

    Returns:
        List of forecasted risk scores for each future horizon step.
    """
    if len(values) < window:
        window = len(values)
    ma = sum(values[-window:]) / window
    return ma


def forecast_risk(control_id: str, days: int = 30, forecast_horizon: int = 7) -> List[Tuple[datetime.date, float]]:
    """
    Generate future risk forecasts for a control based on historical data.

    Args:
        control_id: Control identifier.
        days: Number of past days to consider.
        forecast_horizon: Number of future days to forecast.

    Returns:
        List of (future_date, predicted_risk) tuples.
    """
    history = fetch_historical_risk(control_id, days)
    # Extract just scores
    scores = [s for _, s in history]
    # Compute baseline forecast value using moving average
    base_forecast = simple_moving_average(scores, window=min(7, len(scores)))

    forecasts = []
    last_date = history[-1][0]
    # For simplicity, assume flat forecast at moving average
    for i in range(1, forecast_horizon + 1):
        future_date = last_date + datetime.timedelta(days=i)
        # add small random jitter to forecasts
        pred = min(max(base_forecast + random.uniform(-0.02, 0.02), 0.0), 1.0)
        forecasts.append((future_date, round(pred, 3)))
    return forecasts


def simulate_policy_change(
    control_id: str,
    baseline_days: int,
    horizon: int,
    adjustment_function: Callable[[float], float]
) -> List[Tuple[datetime.date, float]]:
    """
    Simulate a policy or process improvement that adjusts risk scores.

    Args:
        control_id: Control identifier.
        baseline_days: Days of historical data to fetch.
        horizon: Forecast horizon.
        adjustment_function: Function to modify base forecast (e.g., lambda x: x*0.8).

    Returns:
        List of (future_date, simulated_risk) tuples.
    """
    base_forecasts = forecast_risk(control_id, baseline_days, horizon)
    simulated = []
    for date, risk in base_forecasts:
        sim_risk = min(max(adjustment_function(risk), 0.0), 1.0)
        simulated.append((date, round(sim_risk, 3)))
    return simulated


# Example script usage
if __name__ == '__main__':
    print("=== Forecasting Risk for AC-2 ===")
    for d, r in forecast_risk('AC-2', days=30, forecast_horizon=7):
        print(f"{d}: {r}")
    print("=== Simulate 10% Improvement ===")
    for d, r in simulate_policy_change('AC-2', 30, 7, lambda x: x * 0.9):
        print(f"{d}: {r}")
