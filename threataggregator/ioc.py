import asyncio
import ipaddress
import os
from typing import Dict, List

import aiohttp


async def vt_check_ip(ip: str, session: aiohttp.ClientSession, api_key: str) -> Dict:
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": api_key}
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            return {"source": "VirusTotal", "error": resp.status}
        data = await resp.json()
        stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
        return {
            "source": "VirusTotal",
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
        }


async def abuseipdb_check(ip: str, session: aiohttp.ClientSession, api_key: str) -> Dict:
    url = "https://api.abuseipdb.com/api/v2/check"
    params = {"ipAddress": ip, "maxAgeInDays": "90"}
    headers = {"Key": api_key, "Accept": "application/json"}
    async with session.get(url, params=params, headers=headers) as resp:
        if resp.status != 200:
            return {"source": "AbuseIPDB", "error": resp.status}
        data = await resp.json()
        abuse_confidence = data.get("data", {}).get("abuseConfidenceScore", 0)
        return {"source": "AbuseIPDB", "abuse_confidence": abuse_confidence}


async def otx_check_ip(ip: str, session: aiohttp.ClientSession, api_key: str) -> Dict:
    url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
    headers = {"X-OTX-API-KEY": api_key}
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            return {"source": "OTX", "error": resp.status}
        data = await resp.json()
        pulses = len(data.get("pulse_info", {}).get("pulses", []))
        return {"source": "OTX", "pulse_count": pulses}


async def talos_check_ip(ip: str, session: aiohttp.ClientSession) -> Dict:
    url = f"https://talosintelligence.com/sb_ip_query?query={ip}"
    async with session.get(url) as resp:
        if resp.status != 200:
            return {"source": "Talos", "error": resp.status}
        data = await resp.json()
        return {
            "source": "Talos",
            "threat_level": data.get("response", {}).get("threat_level", "unknown"),
        }


async def check_ip(ip: str, vt_key: str, abuse_key: str, otx_key: str) -> List[Dict]:
    async with aiohttp.ClientSession() as session:
        tasks = []
        if vt_key:
            tasks.append(vt_check_ip(ip, session, vt_key))
        if abuse_key:
            tasks.append(abuseipdb_check(ip, session, abuse_key))
        if otx_key:
            tasks.append(otx_check_ip(ip, session, otx_key))
        tasks.append(talos_check_ip(ip, session))
        return await asyncio.gather(*tasks)


def validate_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
