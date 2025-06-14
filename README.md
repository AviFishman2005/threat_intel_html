# Threat Intelligence HTML

This single-page app shows basic threat intelligence information relevant to Israel.

## Features

- **Israel Attack Stats** – Fetches current attack statistics for Israel from the SANS Internet Storm Center API.
- **Latest Threat News** – Displays summaries from the SANS ISC RSS feed.
- **AI Chatbot** – Uses OpenAI's API to answer questions about the latest news.

## Usage

1. Open `index.html` in a browser. It can be hosted statically (e.g. GitHub Pages) or opened directly.
2. Click **Refresh** to load current stats.
3. Click **Load News** to populate the news section.
4. Enter your OpenAI API key in the field provided to enable the chatbot and ask questions about the latest reports.

The application stores the API key in `localStorage` on your browser so you don't need to re-enter it each time.

## Live Threat Feed Aggregator

Run `python threat_feed_aggregator.py` to continuously display the latest items from several threat feeds. Requires packages in `requirements.txt`.

`async_threat_feed_aggregator.py` performs the same task using `aiohttp` to
fetch all feeds concurrently for faster updates and includes additional sources.


## Indicator Reputation Checker

Use `ioc_checker.py` to query multiple threat intelligence sources for a given IP address. The script checks VirusTotal, AbuseIPDB, AlienVault OTX, and Cisco Talos simultaneously. API keys for each service can be supplied via environment variables `VT_API_KEY`, `ABUSEIPDB_API_KEY`, and `OTX_API_KEY`.

Example:

```bash
export VT_API_KEY=YOUR_KEY
python ioc_checker.py 8.8.8.8
```

