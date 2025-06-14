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
