import argparse
import asyncio
import os

from .feeds import DEFAULT_FEEDS, gather_entries as gather_feed_entries, display_entries as display_feed_entries
from .readme import extract_source_urls, gather_entries as gather_readme_entries, display_entries as display_readme_entries
from .ioc import check_ip, validate_ip


async def run_feed_loop(interval: int) -> None:
    seen_links = set()
    while True:
        entries = await gather_feed_entries(DEFAULT_FEEDS)
        if entries:
            display_feed_entries(entries, seen_links)
        await asyncio.sleep(interval)


async def run_readme_once() -> None:
    sources = extract_source_urls()
    if not sources:
        print("No sources found in README")
        return
    entries = await gather_readme_entries(sources)
    if entries:
        display_readme_entries(entries)


async def run_ioc_check(ip: str) -> None:
    vt_key = os.getenv("VT_API_KEY")
    abuse_key = os.getenv("ABUSEIPDB_API_KEY")
    otx_key = os.getenv("OTX_API_KEY")
    results = await check_ip(ip, vt_key, abuse_key, otx_key)
    for res in results:
        if "error" in res:
            print(f"{res['source']}: error {res['error']}")
        else:
            print(f"{res['source']}: {res}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Threat Aggregator Toolkit")
    sub = parser.add_subparsers(dest="command")

    feeds_p = sub.add_parser("feeds", help="Stream common threat feeds")
    feeds_p.add_argument("--interval", type=int, default=300, help="Refresh interval in seconds")

    sub.add_parser("sources", help="Display entries from README sources")

    ioc_p = sub.add_parser("ioc", help="Check IP reputation")
    ioc_p.add_argument("ip", help="IP address to check")

    args = parser.parse_args()

    if args.command == "feeds":
        asyncio.run(run_feed_loop(args.interval))
    elif args.command == "sources":
        asyncio.run(run_readme_once())
    elif args.command == "ioc":
        if not validate_ip(args.ip):
            print("Invalid IP address")
            return
        asyncio.run(run_ioc_check(args.ip))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
