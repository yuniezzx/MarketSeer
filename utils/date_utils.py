import pandas as pd
from utils.config_loader import load_config
import exchange_calendars as ecals

def get_trade_days() -> list:
    """
    从配置的 start_date 到今天，获取所有交易日
    """
    config = load_config()
    start_date_str = config["event"]["start_date"]
    start_date = pd.to_datetime(start_date_str).normalize()
    today = pd.Timestamp.now().normalize()

    sse = ecals.get_calendar("XSHG")
    sessions = sse.sessions_in_range(start_date, today)

    return [d.strftime("%Y-%m-%d") for d in sessions]


