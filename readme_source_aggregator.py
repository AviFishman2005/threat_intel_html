"""Backward compatible wrapper for the new threataggregator package."""

import asyncio
from threataggregator.readme import extract_source_urls, gather_entries, display_entries


async def _main() -> None:
    sources = extract_source_urls()
    if not sources:
        print("No sources found in README")
        return
    entries = await gather_entries(sources)
    if entries:
        display_entries(entries)


if __name__ == "__main__":
    asyncio.run(_main())
