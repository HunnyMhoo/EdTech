from datetime import datetime, timedelta, timezone

TARGET_TIMEZONE = timezone(timedelta(hours=7))

def get_utc7_today_date() -> datetime.date:
    """Calculates today's date in UTC+7."""
    return datetime.now(TARGET_TIMEZONE).date()

def get_current_time_in_target_timezone() -> datetime:
    """Gets the current time in the target timezone."""
    return datetime.now(TARGET_TIMEZONE) 