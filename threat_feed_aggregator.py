import feedparser
from bs4 import BeautifulSoup
import time
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table

# List of RSS feeds to poll. Only feeds that reliably return valid XML are
# included to ensure new content is fetched on every run.
FEEDS = {
    "Kaspersky": "https://securelist.com/feed/",
    "Cisco Talos": "https://blog.talosintelligence.com/rss",
    "BleepingComputer": "https://www.bleepingcomputer.com/feed/",
    "The Hacker News": "https://feeds.feedburner.com/TheHackersNews",
    "SecurityWeek": "https://www.securityweek.com/feed/",
    "Dark Reading": "https://www.darkreading.com/rss.xml",
    "KrebsOnSecurity": "https://krebsonsecurity.com/feed/",
    "CISA ICS": "https://www.cisa.gov/uscert/ncas/all.xml",
}

REFRESH_INTERVAL = 300  # 5 minutes

console = Console()


def clean_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()


def fetch_feed(name: str, url: str):
    try:
        feed = feedparser.parse(url)
        if getattr(feed, "bozo", 0):
            console.print(
                f"[yellow]Warning: {name} feed parsing issue: {feed.bozo_exception}[/yellow]"
            )
        return feed
    except Exception as e:
        console.print(f"[red]Failed to fetch {name} feed: {e}[/red]")
        return None


def gather_entries():
    entries = []
    for name, url in FEEDS.items():
        feed = fetch_feed(name, url)
        if not feed or not feed.entries:
            continue
        for entry in feed.entries:
            published = None
            if 'published_parsed' in entry and entry.published_parsed:
                published = datetime.fromtimestamp(
                    time.mktime(entry.published_parsed), tz=timezone.utc
                )
            entries.append({
                'title': entry.get('title', 'No title'),
                'link': entry.get('link', ''),
                'summary': clean_html(entry.get('summary', '')),
                'published': published,
                'source': name
            })
    return entries


def display_entries(entries, seen_links):
    table = Table(title=f"Threat Intelligence Feeds ({datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')})")
    table.add_column("Source")
    table.add_column("Published")
    table.add_column("Title")
    table.add_column("Link")

    new_entries = []
    for entry in sorted(entries, key=lambda x: x['published'] or datetime.now(timezone.utc), reverse=True):
        if entry['link'] in seen_links:
            continue
        seen_links.add(entry['link'])
        new_entries.append(entry)
        if len(new_entries) >= 10:
            break

    for entry in new_entries:
        published = entry['published'].strftime('%Y-%m-%d %H:%M') if entry['published'] else 'Unknown'
        table.add_row(entry['source'], published, entry['title'], entry['link'])

    console.clear()
    console.print(table)


if __name__ == "__main__":
    seen_links = set()
    while True:
        try:
            entries = gather_entries()
            if entries:
                display_entries(entries, seen_links)
            else:
                console.print("[yellow]No entries fetched.[/yellow]")
        except KeyboardInterrupt:
            console.print("Exiting...")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        time.sleep(REFRESH_INTERVAL)
