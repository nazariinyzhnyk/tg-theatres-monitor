import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from monitor.notifier import send_telegram_message
from monitor.parser import parse_all
from monitor.utils.load_cfg import load_yaml_config
from monitor.utils.logger import logger

load_dotenv()


def check_env_vars() -> None:
    """
    Ensure required environment variables are set.

    Raises:
        EnvironmentError: If any required environment variable is missing.
    """
    required_vars = ["BOT_ID", "CHAT_ID"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


def format_theatre_schedule_html(items: dict, tz: str = "Europe/Prague", dt_parsable: bool = False) -> str:
    """
    Format theatre schedule into a Telegram-ready HTML string.
    Each play is bold, shows are sorted by date ascending,
    and links are proper <a href="">.

    Args:
        items (dict): List of shows with 'title', 'datetime', and 'link'.
        tz (str): Timezone for datetime conversion.
        dt_parsable (bool): Whether the datetime strings are ISO 8601 parseable.

    Returns:
        str: Formatted HTML string.
    """
    parsed = []
    for it in items:
        title = " ".join(it["title"].split())
        dt = it["datetime"]
        if dt_parsable:
            dt = datetime.fromisoformat(it["datetime"]).astimezone(ZoneInfo(tz))
        parsed.append({"title": title, "dt": dt, "link": it["link"]})

    parsed.sort(key=lambda x: x["dt"])

    grouped: dict = {}
    for row in parsed:
        if row["title"] not in grouped:
            grouped[row["title"]] = []
        grouped[row["title"]].append(row)

    lines = []
    for title, shows in grouped.items():
        lines.append(f"<b>{title}</b>")
        for s in shows:
            date_str = s["dt"]
            if dt_parsable:
                date_str = date_str.strftime("%a, %d %b %H:%M")

            lines.append(f"- {date_str} → <a href=\"{s['link']}\">Detail</a>")
        lines.append("")

    return "\n".join(lines).strip()


def main() -> None:
    check_env_vars()

    cfg = load_yaml_config()

    logger.info("Start parsing theatres")
    parsed_theatres_info = parse_all()
    logger.info("Finished parsing theatres")

    for theatre_name, shows in parsed_theatres_info.items():
        theatre_config: dict = next((th for th in cfg["theatres"] if th["name"] == theatre_name), {})

        logger.info(f"Processing theatre: {theatre_name}")
        message = format_theatre_schedule_html(shows, dt_parsable=theatre_config.get("time_parseable", False))
        message = f"<b>{theatre_name}</b>\n\n" + message
        send_telegram_message(os.environ["BOT_ID"], os.environ["CHAT_ID"], message)


if __name__ == "__main__":
    logger.info("Starting the monitoring script...")
    try:
        main()
        logger.info("Monitoring script completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    logger.info("Monitoring script finished.")
