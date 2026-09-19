
from zoneinfo import ZoneInfo
import datetime as dt

def get_today() -> dt.date:
    return dt.datetime.now(ZoneInfo("America/New_York")).date()