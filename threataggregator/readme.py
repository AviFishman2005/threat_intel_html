import asyncio
import re
from datetime import datetime, timezone
from typing import Dict, List

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table


README_FILE = "README.md"
console = Console()


def extract_source_urls() -> Dict[str, str]:
    with open(README_FILE, "r", encoding="utf-8") as f:
        text = f.read()
    match = re.search(r"## Sources(.*?)## ", text, re.S)
    if not match:
        return {}
    html = match.group(1)
    soup = BeautifulSoup(html, "html.parser")
    links: Dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        links[a.get_text(strip=True)] = a["href"]
    return links


async def fetch_feed(name: str, url: str, session: aiohttp.ClientSession):
    try:
        async with session.get(url, timeout=10) as resp:
            data = await resp.read()
        feed = feedparser.parse(data)
        if feed.entries:
            return name, feed
        console.print(f"[yellow]No feed entries for {name}[/yellow]")
        return name, None
    except Exception as e:
        console.print(f"[red]Failed to fetch {name}: {e}[/red]")
        return name, None


async def gather_entries(sources: Dict[str, str]) -> List[Dict]:
    entries: List[Dict] = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_feed(name, url, session) for name, url in sources.items()]
        for name, feed in await asyncio.gather(*tasks):
            if not feed:
                continue
            for entry in feed.entries:
                published = None
                if entry.get("published_parsed"):
                    published = datetime.fromtimestamp(
                        feedparser.mktime_tz(entry.published_parsed), tz=timezone.utc
                    )
                entries.append(
                    {
                        "title": entry.get("title", "No title"),
                        "link": entry.get("link", ""),
                        "summary": BeautifulSoup(entry.get("summary", ""), "html.parser").get_text(),
                        "published": published,
                        "source": name,
                    }
                )
    return entries


def display_entries(entries: List[Dict], title: str = "README Sources"):
    table = Table(
        title=f"{title} ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')})"
    )
    table.add_column("Source")
    table.add_column("Published")
    table.add_column("Title")
    table.add_column("Link")

    for entry in sorted(entries, key=lambda x: x["published"] or datetime.now(timezone.utc), reverse=True)[:10]:
        published = entry["published"].strftime("%Y-%m-%d %H:%M") if entry["published"] else "Unknown"
        table.add_row(entry["source"], published, entry["title"], entry["link"])

    console.clear()
    console.print(table)

