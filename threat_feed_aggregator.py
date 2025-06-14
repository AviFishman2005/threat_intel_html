"""Backward compatible wrapper for the new threataggregator package."""

import asyncio
from threataggregator.feeds import DEFAULT_FEEDS, gather_entries, display_entries


async def _main() -> None:
    seen = set()
    while True:
        entries = await gather_entries(DEFAULT_FEEDS)
        if entries:
            display_entries(entries, seen)
        await asyncio.sleep(300)


if __name__ == "__main__":
    asyncio.run(_main())
