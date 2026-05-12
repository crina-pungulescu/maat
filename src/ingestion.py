# MAAT ingestion pipeline v0.3
# RSS ingestion + JSONL storage

import feedparser
import datetime
import json
from pathlib import Path


RSS_FEEDS = [
    "https://www.timeshighereducation.com/rss",
    "https://www.insidehighered.com/rss/news",
    "https://www.ilsole24ore.com/rss/economia.xml",
    "https://elpais.com/rss/elpais/portada.xml"
]


OUTPUT_FILE = "data/raw/articles.jsonl"


def log(message):
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def fetch_rss_articles():

    articles = []

    for url in RSS_FEEDS:

        log(f"Fetching RSS feed: {url}")

        feed = feedparser.parse(url)

        for entry in feed.entries[:10]:

            article = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "source": url,
                "retrieved_at": datetime.datetime.now().isoformat()
            }

            articles.append(article)

    return articles


def save_articles_jsonl(articles):

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:

        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + "\n")

    log(f"Saved {len(articles)} articles to {OUTPUT_FILE}")


def run_pipeline():

    log("MAAT RSS ingestion started")

    articles = fetch_rss_articles()

    log(f"Collected {len(articles)} articles")

    save_articles_jsonl(articles)

    log("MAAT ingestion complete")


if __name__ == "__main__":
    run_pipeline()
