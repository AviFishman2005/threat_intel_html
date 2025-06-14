import asyncio
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser
import pytz
from rich.console import Console
from rich.table import Table


DEFAULT_FEEDS: Dict[str, str] = {
    "Kaspersky": "https://securelist.com/feed/",
    "Cisco Talos": "https://blog.talosintelligence.com/rss",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "SecurityWeek": "https://www.securityweek.com/feed/",
    "Dark Reading": "https://www.darkreading.com/rss.xml",
    "KrebsOnSecurity": "https://krebsonsecurity.com/feed/",
    "CISA ICS": "https://www.cisa.gov/uscert/ncas/all.xml",
    "Naked Security": "https://nakedsecurity.sophos.com/feed/",
    "Malwarebytes": "https://blog.malwarebytes.com/feed/",
}

console = Console()


def clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


async def fetch_feed(name: str, url: str, session: aiohttp.ClientSession):
    try:
        async with session.get(url) as resp:
            data = await resp.read()
            feed = feedparser.parse(data)
            if getattr(feed, "bozo", 0):
                console.print(
                    f"[yellow]Warning: {name} feed parsing issue: {feed.bozo_exception}[/yellow]"
                )
            return name, feed
    except Exception as e:
        console.print(f"[red]Failed to fetch {name} feed: {e}[/red]")
        return name, None


async def gather_entries(feeds: Dict[str, str]) -> List[Dict]:
    entries: List[Dict] = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(name, url, session) for name, url in feeds.items()]
        for name, feed in await asyncio.gather(*tasks):
            if not feed or not feed.entries:
                continue
            for entry in feed.entries:
                published = None
                published_str = entry.get("published") or entry.get("pubDate")
                if published_str:
                    try:
                        dt = date_parser.parse(published_str)
                        published = dt.astimezone(pytz.utc)
                    except Exception:
                        pass
                entries.append(
                    {
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link", ""),
                        "summary": clean_html(entry.get("summary", "")),
                        "published": published,
                        "source": name,
                    }
                )
    return entries


def display_entries(entries: List[Dict], seen_links: set, title: str = "Threat Feeds"):
    table = Table(
        title=f"{title} ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')})"
    )
    table.add_column("Source")
    table.add_column("Published")
    table.add_column("Title")
    table.add_column("Link")

    new_entries: List[Dict] = []
    for entry in sorted(entries, key=lambda x: x["published"] or datetime.now(timezone.utc), reverse=True):
        if entry["link"] in seen_links:
            continue
        seen_links.add(entry["link"])
        new_entries.append(entry)
        if len(new_entries) >= 10:
            break

    for entry in new_entries:
        published = entry["published"].strftime("%Y-%m-%d %H:%M") if entry["published"] else "Unknown"
        table.add_row(entry["source"], published, entry["title"], entry["link"])

    console.clear()
    console.print(table)
