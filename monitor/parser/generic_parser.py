import time

import requests
from bs4 import BeautifulSoup, ResultSet, Tag

from monitor.utils.logger import logger


def first_text(el: Tag | None) -> str:
    """
    Extract and return the stripped text from a BeautifulSoup element.

    Parameters
    ----------
    el: Tag | None
        The BeautifulSoup element to extract text from.

    Returns
    -------
    str
        The stripped text content of the element, or an empty string if the element is None.
    """
    if not el:
        return ""
    return el.get_text(strip=True)


def fetch(
    url: str,
    requests_timeout: int = 10,
    backoff_time: int = 1,
    n_retries: int = 3,
) -> BeautifulSoup:
    """
    Fetch and parse HTML content from a URL with retries and exponential backoff.

    Parameters
    ----------
    url: str
        The URL to fetch.
    requests_timeout: int
        Timeout for the requests in seconds.
    backoff_time: int
        Initial backoff time in seconds.
    n_retries: int
        Number of retries on failure.

    Returns
    -------
    BeautifulSoup
        Parsed HTML content.

    Raises
    ------
    Exception
        If all retries fail.
    """

    for attempt in range(n_retries):
        try:
            r = requests.get(url, timeout=requests_timeout)
            r.raise_for_status()
            return BeautifulSoup(r.text, "lxml")

        except Exception as e:
            logger.info("Error fetching %s: %s", url, e)
            time.sleep(backoff_time * (attempt + 1))

    raise Exception(f"Failed to fetch {url} after {n_retries} attempts")


def parse_performances(
    elements: ResultSet[Tag],
    time_tag_name: str,
    performance_link_name: str,
) -> list[dict]:
    """
    Parse performance elements to extract datetime, title, and link.

    Parameters
    ----------
    elements: list[BeautifulSoup]
        List of BeautifulSoup elements representing performances.
    time_tag_name: str
        CSS selector for the time tag.
    performance_link_name
        CSS selector for the performance link tag.

    Returns
    -------
    list[dict]
        List of dictionaries with keys 'datetime', 'title', and 'link'.
    """
    performances = []
    for perf in elements:
        time_tag = perf.select_one(time_tag_name)
        datetime = time_tag["datetime"] if time_tag and time_tag.has_attr("datetime") else first_text(time_tag)

        title_tag = perf.select_one(performance_link_name)
        title = first_text(title_tag)
        link = title_tag["href"] if title_tag and title_tag.has_attr("href") else None

        performances.append({"datetime": datetime, "title": title, "link": link})

    return performances


def fetch_and_parse(
    url: str,
    elements_name: str,
    time_tag_name: str,
    performance_link_name: str,
) -> list[dict]:
    """
    Fetch a URL and parse performance data.
    Parameters
    ----------

    url: str
        The URL to fetch data from.
    elements_name: str
        CSS selector for the performance elements.
    time_tag_name: str
        CSS selector for the time tag.
    performance_link_name: str
        CSS selector for the performance link tag.

    Returns
    -------
    list[dict]
        List of dictionaries with parsed performance data.
    """

    soup = fetch(url)
    elements = soup.select(elements_name)
    parsed_performances = parse_performances(
        elements, time_tag_name=time_tag_name, performance_link_name=performance_link_name
    )

    return parsed_performances
