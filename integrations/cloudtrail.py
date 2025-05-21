"""
integrations/cloudtrail.py

Continuous Evidence Collection & Validation for RegScale CCM

This connector ingests AWS CloudTrail events as evidence for compliance monitoring, and validates
that the retrieved events conform to expected schemas and timestamp coverage. It is part of the
"Continuous Evidence Collection & Validation" feature in `docs/FEATURE_PROPOSALS.md`.

Key functions:
- `fetch_cloudtrail_events(start_date, end_date)`: Mock retrieval of CloudTrail logs between dates.
- `validate_event_schema(event)`: Ensures each event contains required fields (e.g., EventTime, EventName).
- `validate_coverage(events, expected_window_days)`: Confirms logs cover each day in the window (no missing intervals).
- `collect_cloudtrail_evidence(start_date, end_date)`: Orchestrates fetch + validation, returning only clean evidence.

Why this approach?
- **Automated Ingestion:** Eliminates manual uploads of CloudTrail logs, ensuring near-real-time evidence.
- **Quality Assurance:** Early detection of missing or malformed logs prevents audit gaps.
- **Modular & Extensible:** Additional connectors (e.g., `integrations/qualys.py`) follow the same pattern.

Usage:
    from integrations.cloudtrail import collect_cloudtrail_evidence
    evidence = collect_cloudtrail_evidence('2025-04-01', '2025-04-07')
    for evt in evidence:
        print(evt)
"""

import datetime
import random

# Required fields for valid CloudTrail event
REQUIRED_FIELDS = ["EventTime", "EventName", "Username", "AWSRegion", "SourceIPAddress"]


def fetch_cloudtrail_events(start_date: str, end_date: str) -> list:
    """
    Mock function to fetch CloudTrail events between two dates (inclusive).

    Args:
        start_date: 'YYYY-MM-DD'
        end_date: 'YYYY-MM-DD'
    Returns:
        List of event dicts with keys matching AWS CloudTrail schema.
    """
    sd = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    ed = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    delta = (ed - sd).days + 1
    events = []
    # Generate mock events: two per day, plus random missing days
    for i in range(delta):
        day = sd + datetime.timedelta(days=i)
        # simulate missing logs 10% of days
        if random.random() < 0.1:
            continue
        for _ in range(2):
            evt = {
                "EventTime": day.isoformat() + "T12:34:56Z",
                "EventName": random.choice(["CreateUser", "DeleteUser", "UpdateBucketPolicy"]),
                "Username": random.choice(["alice", "bob", "charlie"]),
                "AWSRegion": random.choice(["us-east-1", "us-west-2"]),
                "SourceIPAddress": f"192.0.2.{random.randint(1,254)}",
                # occasional missing field
                **({} if random.random() < 0.95 else {"Username": None})
            }
            events.append(evt)
    return events


def validate_event_schema(event: dict) -> bool:
    """
    Check that a CloudTrail event contains all REQUIRED_FIELDS and they are non-empty.

    Args:
        event: dict representing a CloudTrail event
    Returns:
        True if valid schema, False otherwise
    """
    for field in REQUIRED_FIELDS:
        if field not in event or not event[field]:
            return False
    return True


def validate_coverage(events: list, expected_window_days: int) -> bool:
    """
    Ensure that we have at least one event per day for the expected window.

    Args:
        events: list of valid event dicts
        expected_window_days: int, number of days we expect coverage for
    Returns:
        True if coverage is complete, False if any day is missing events
    """
    dates_seen = set()
    for evt in events:
        # parse date portion
        date_str = evt["EventTime"].split("T")[0]
        dates_seen.add(date_str)
    return len(dates_seen) >= expected_window_days


def collect_cloudtrail_evidence(start_date: str, end_date: str) -> list:
    """
    Full pipeline to collect and validate CloudTrail evidence.

    Args:
        start_date: 'YYYY-MM-DD'
        end_date: 'YYYY-MM-DD'

    Returns:
        List of validated CloudTrail event dicts
    """
    raw_events = fetch_cloudtrail_events(start_date, end_date)
    valid_events = [evt for evt in raw_events if validate_event_schema(evt)]
    # Calculate expected days
    sd = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    ed = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    expected_days = (ed - sd).days + 1
    if not validate_coverage(valid_events, expected_days):
        raise RuntimeError(f"Missing CloudTrail coverage between {start_date} and {end_date}")
    return valid_events


def run_example():
    # Example usage of evidence collection pipeline
    try:
        evidence = collect_cloudtrail_evidence('2025-04-01', '2025-04-07')
        print(f"Collected {len(evidence)} valid CloudTrail events.")
    except RuntimeError as e:
        print("Error in evidence coverage:", e)


if __name__ == "__main__":
    run_example()
