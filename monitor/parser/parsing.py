import os

import yaml

from monitor.parser.generic_parser import fetch_and_parse
from monitor.utils.logger import logger


def parse_all(conf_file_path: str | None = None) -> dict:
    """
    Parse all theatres as per configuration file.

    Parameters
    ----------
    conf_file_path: str | None
        Path to the configuration file. If None, defaults to 'theatres_cfg.yaml' in the current directory.

    Returns
    -------
    dict
        A dictionary with theatre names as keys and lists of parsed performance data as values.
    """
    if conf_file_path is None:
        conf_file_path = os.path.join(os.path.dirname(__file__), "theatres_cfg.yaml")

    if not os.path.exists(conf_file_path):
        logger.error(f"Config file not found within path: {conf_file_path}")
        raise FileNotFoundError(f"Config file not found within path: {conf_file_path}")

    with open(conf_file_path, "r") as conf_file_path:  # type: ignore
        cfg = yaml.safe_load(conf_file_path)

    results = {}
    for theatre in cfg.get("theatres", []):

        theatre_name = theatre.get("name", "unknown_theatre")
        base_url = theatre.get("base_url")
        program_url = theatre.get("program_url")
        selectors = theatre.get("selectors", {})
        if not program_url or not selectors:
            logger.warning(f"Skipping theatre '{theatre_name}' due to missing URL or selectors.")
            continue

        logger.info(f"Parsing theatre: {theatre_name} from URL: {program_url}")
        parsed_data = fetch_and_parse(
            url=program_url,
            elements_name=selectors["elements"],
            time_tag_name=selectors["time"],
            performance_link_name=selectors["link"],
        )

        parsed_data = parsed_data[: cfg["general"]["results_per_theatre"]]
        for item in parsed_data:
            if item["link"] and not item["link"].startswith("http"):
                item["link"] = base_url.rstrip("/") + "/" + item["link"].lstrip("/")

        results[theatre_name] = parsed_data
        logger.info(f"Successfully parsed data for theatre: {theatre_name}")

    return results


def main() -> None:
    try:
        res = parse_all()
        print(res)
    except Exception as e:
        logger.error(f"Error during parsing: {e}")


if __name__ == "__main__":
    main()
