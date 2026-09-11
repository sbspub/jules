"""Read-only providers for live paper-mode analysis inputs."""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

import requests


class RealDataError(RuntimeError):
    """Raised when a required real analysis input cannot be retrieved."""


_HEADERS = {"User-Agent": "shargent/1.0 (paper-analysis)"}


def fetch_news(symbol: str, limit: int = 8) -> list[dict[str, str]]:
    """Fetch recent, attributable headlines for an NSE symbol from Google News RSS."""
    url = "https://news.google.com/rss/search?q=" + quote_plus(f"{symbol} NSE stock") + "&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        response = requests.get(url, headers=_HEADERS, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
    except (requests.RequestException, ET.ParseError) as exc:
        raise RealDataError(f"could not retrieve news for {symbol}: {exc}") from exc
    items = [
        {"title": (item.findtext("title") or "").strip(), "source": (item.findtext("source") or "").strip(), "url": (item.findtext("link") or "").strip()}
        for item in root.findall("./channel/item")[:limit]
        if (item.findtext("title") or "").strip()
    ]
    if not items:
        raise RealDataError(f"no current news items were returned for {symbol}")
    return items


def _metric(page: str, label: str) -> float | None:
    label_pattern = re.escape(label).replace(r"\ ", r"\s+")
    match = re.search(rf'<span class="name">\s*{label_pattern}\s*</span>.*?<span class="number">\s*([\d.]+)\s*</span>', page, re.IGNORECASE | re.DOTALL)
    return float(match.group(1)) if match else None


def fetch_fundamentals(symbol: str, current_price: float) -> dict[str, float]:
    """Fetch publicly reported valuation and return-on-equity metrics."""
    url = f"https://www.screener.in/company/{quote_plus(symbol.upper())}/consolidated/"
    try:
        response = requests.get(url, headers=_HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RealDataError(f"could not retrieve fundamentals for {symbol}: {exc}") from exc
    page = html.unescape(response.text)
    pe, book_value, roe = _metric(page, "Stock P/E"), _metric(page, "Book Value"), _metric(page, "ROE")
    if pe is None and book_value is None and roe is None:
        raise RealDataError(f"no fundamental metrics were returned for {symbol}")
    values: dict[str, float] = {}
    if pe is not None:
        values["pe_ratio"] = pe
    if book_value and book_value > 0:
        values["pb_ratio"] = round(current_price / book_value, 2)
    if roe is not None:
        values["roe_pct"] = roe
    return values
