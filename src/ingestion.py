# MAAT ingestion pipeline v0.2
# Live RSS ingestion

import feedparser
import datetime


RSS_FEEDS = [
    # English
    "https://www.timeshighereducation.com/rss",
    "https://www.insidehighered.com/rss/news",

    # Italy
    "https://www.ilsole24ore.com/rss/economia.xml",

    # France
    "https://www.lemonde.fr/en/rss/une.xml",

    # Spain
    "https://elpais.com/rss/elpais/portada.xml"
]


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
                "summary": entry.get("summary", "")
            }

            articles.append(article)

    return articles


def display_articles(articles):

    for i, a in enumerate(articles, 1):

        print(f"\nArticle {i}")
        print("Title:", a["title"])
        print("Published:", a["published"])
        print("Link:", a["link"])


def run_pipeline():

    log("MAAT RSS ingestion started")

    articles = fetch_rss_articles()

    log(f"Collected {len(articles)} articles")

    display_articles(articles)

    log("MAAT ingestion complete")


if __name__ == "__main__":
    run_pipeline()
