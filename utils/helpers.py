from datetime import datetime, timezone, timedelta

def parse_duration(duration_str: str) -> int | None:
    if not duration_str or not isinstance(duration_str, str):
        return None
    duration_str = duration_str.strip()
    if len(duration_str) < 2:
        return None

    unit = duration_str[-1].lower()
    number_part = duration_str[:-1]

    if not number_part.isdigit():
        return None
    
    value = int(number_part)

    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400

    return None

def calculate_timeout(seconds: int | float) -> datetime | None:
    if not isinstance(seconds, (int, float)):
        return None
    if seconds <= 0:
        raise ValueError("Timeout duration cannot be negative.")

    return datetime.now(timezone.utc) + timedelta(seconds=seconds)
