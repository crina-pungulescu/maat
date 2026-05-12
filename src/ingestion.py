# MAAT ingestion pipeline (v0.1 dummy scaffold)

import datetime


def log(message):
    """Simple logging utility for MAAT pipeline"""
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def fetch_sources():
    """
    Dummy data source.
    Will later become RSS feeds + multilingual scraping.
    """
    return [
        {
            "title": "University reforms announced in Europe",
            "date": str(datetime.date.today()),
            "link": "https://example.com/article1",
            "language": "en"
        },
        {
            "title": "Accreditation changes in higher education systems",
            "date": str(datetime.date.today()),
            "link": "https://example.com/article2",
            "language": "en"
        }
    ]


def process_articles(articles):
    """
    Placeholder for filtering + classification.
    """
    processed = []

    for a in articles:
        if "university" in a["title"].lower() or "education" in a["title"].lower():
            processed.append(a)

    return processed


def run_pipeline():
    log("MAAT ingestion started")

    articles = fetch_sources()
    log(f"Fetched {len(articles)} articles")

    processed = process_articles(articles)
    log(f"Filtered down to {len(processed)} relevant articles")

    for i, a in enumerate(processed, 1):
        print(f"\nArticle {i}")
        print("Title:", a["title"])
        print("Date:", a["date"])
        print("Link:", a["link"])
        print("Language:", a["language"])

    log("MAAT ingestion complete")


if __name__ == "__main__":
    run_pipeline()
