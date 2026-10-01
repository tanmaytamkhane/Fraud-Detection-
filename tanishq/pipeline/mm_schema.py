"""Schema checks for raw money movement events."""
from math import isfinite

REQUIRED_FIELDS = ("transfer_id", "timestamp", "sender", "receiver", "amount")


def validate_transfer(event):
    missing = [k for k in REQUIRED_FIELDS if k not in event or event[k] is None]
    if missing:
        raise ValueError(f"Missing raw transfer fields: {missing}")
    if not isfinite(float(event["amount"])) or float(event["amount"]) < 0:
        raise ValueError("amount must be finite and nonnegative")
    if not str(event["sender"]) or not str(event["receiver"]):
        raise ValueError("sender and receiver are required")
    return event
