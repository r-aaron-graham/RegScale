"""
scripts/detect_drift.py

Proactive Risk & Drift Detection for RegScale CCM

This module implements time-series drift detection on continuous controls monitoring data. It is part of the "Proactive Risk & Drift Detection"
feature outlined in `docs/FEATURE_PROPOSALS.md`.

Key functions:
- `fetch_snapshots()`: Mock or real interface to pull historical control metrics (e.g., misconfig counts).
- `compute_time_series(metrics)`: Convert raw snapshots into a time-series structure.
- `detect_drift_zscore(ts, window, threshold)`: Identify anomalies in the time series using rolling z-score.
- `generate_alerts(drift_points)`: Formulate actionable alerts for any detected drift.

Why this approach?
- **Early Warning:** Detects config drifts or unusual spikes before audits flag them.
- **Automated Alerts:** Integrates with alerting/workflow systems (e.g., Jira/ServiceNow) automatically.
- **Cost Efficient:** Simple statistical methods (z-score) run cheaply on historical data.
- **Modular & Extendable:** Replace z-score with other methods (e.g., change-point detection) as needed.

Usage:
    from scripts.detect_drift import run_drift_detection
    alerts = run_drift_detection()
    for alert in alerts:
        print(alert)
"""

import datetime
import random
from collections import deque


def fetch_snapshots(days=30):
    """
    Mock function to retrieve daily misconfiguration counts for the last `days` days.
    In a real implementation, this would call cloud provider APIs or SIEM logs.

    Returns:
        List of tuples (date: datetime.date, value: int)
    """
    today = datetime.date.today()
    snapshots = []
    # Generate mock data: stable around 5, occasional drift spike
    for i in range(days, 0, -1):
        date = today - datetime.timedelta(days=i)
        # Simulate occasional drift: every 10 days, random spike
        base = 5
        if i % 10 == 0:
            value = base + random.randint(5, 15)
        else:
            value = base + random.randint(-1, 2)
        snapshots.append((date, max(value, 0)))
    return snapshots


def compute_time_series(snapshots):
    """
    Convert snapshot list into two parallel lists for dates and values.

    Args:
        snapshots: List of (date, value)

    Returns:
        dates: List[datetime.date]
        values: List[int]
    """
    dates, values = zip(*snapshots)
    return list(dates), list(values)


def detect_drift_zscore(dates, values, window=7, threshold=2.0):
    """
    Rolling z-score drift detection:
    - Computes mean and std over a sliding window of `window` days.
    - Flags points where |value - mean| > threshold * std.

    Args:
        dates: List of dates
        values: List of corresponding metric values
        window: int, sliding window size
        threshold: float, z-score threshold to flag an anomaly

    Returns:
        List of tuples (date, value, z_score) for drift points
    """
    drift_points = []
    buf = deque(maxlen=window)
    for i in range(len(values)):
        buf.append(values[i])
        if len(buf) < window:
            continue
        mean = sum(buf) / window
        # population std dev
        var = sum((x - mean) ** 2 for x in buf) / window
        std = var ** 0.5
        if std == 0:
            continue
        z_score = (values[i] - mean) / std
        if abs(z_score) > threshold:
            drift_points.append((dates[i], values[i], round(z_score, 2)))
    return drift_points


def generate_alerts(drift_points):
    """
    Generate human-readable alerts from detected drift points.

    Args:
        drift_points: List of (date, value, z_score)

    Returns:
        List of alert strings
    """
    alerts = []
    for date, value, z in drift_points:
        msg = (f"[ALERT] On {date.isoformat()}, metric spiked to {value} "
               f"(z-score={z}). Investigate possible configuration drift.")
        alerts.append(msg)
    return alerts


def run_drift_detection():
    """
    Orchestrates the full drift detection pipeline:
      1. Fetch snapshots
      2. Compute time series
      3. Detect drift via z-score
      4. Generate alerts

    Returns:
        List of alert messages
    """
    snapshots = fetch_snapshots()
    dates, values = compute_time_series(snapshots)
    drift_points = detect_drift_zscore(dates, values)
    alerts = generate_alerts(drift_points)
    return alerts


if __name__ == "__main__":
    for alert in run_drift_detection():
        print(alert)
