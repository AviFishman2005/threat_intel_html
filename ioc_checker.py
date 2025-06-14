"""Backward compatible wrapper for the new threataggregator package."""

import asyncio
import os
import sys
from threataggregator.ioc import validate_ip, check_ip


async def _main(ip: str) -> None:
    if not validate_ip(ip):
        print("Invalid IP address")
        return
    vt_key = os.getenv("VT_API_KEY")
    abuse_key = os.getenv("ABUSEIPDB_API_KEY")
    otx_key = os.getenv("OTX_API_KEY")
    results = await check_ip(ip, vt_key, abuse_key, otx_key)
    for res in results:
        if "error" in res:
            print(f"{res['source']}: error {res['error']}")
        else:
            print(f"{res['source']}: {res}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ioc_checker.py <ip>")
    else:
        asyncio.run(_main(sys.argv[1]))
