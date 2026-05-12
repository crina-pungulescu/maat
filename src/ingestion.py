# MAAT ingestion pipeline v0.3
# RSS ingestion + JSONL storage

import feedparser
import datetime
import json
from pathlib import Path


RSS_FEEDS = [

    # 🇺🇸 🇬🇧 English (US/UK higher ed focus)
    "https://www.insidehighered.com/rss/news",
    "https://www.timeshighereducation.com/rss",
    "https://www.chronicle.com/rss",
    "https://www.universityworldnews.com/rss.php",

    # 🇩🇪 German-speaking Europe
    "https://www.forschung-und-lehre.de/rss.xml",
    "https://www.diezeit.de/index.rss",

    # 🇫🇷 France
    "https://www.letudiant.fr/rss/actualites.xml",
    "https://www.lemonde.fr/enseignement-superieur/rss_full.xml",

    # 🇪🇸 Spain
    "https://www.universia.net/rss.xml",
    "https://elpais.com/rss/elpais/educacion.xml",

    # 🇮🇹 Italy
    "https://www.ilsole24ore.com/rss/economia.xml",
    "https://www.roars.it/feed/",

    # 🇳🇱 Netherlands / EU academia
    "https://www.scienceguide.nl/feed/",

    # 🌍 Global policy / research signals
    "https://www.oecd.org/education/rss.xml"
]


OUTPUT_FILE = "data/raw/articles.jsonl"

def is_relevant(article):

    text = (
        article.get("title", "") + " " +
        article.get("summary", "")
    ).lower()

    # 🌍 multilingual keyword signals (soft filter)
    keyword_signals = [
        "university", "università", "université", "universidad",
        "universität", "învățământ", "educación", "enseignement",
        "higher education", "academic", "facultad", "faculté",
        "student", "studente", "étudiant", "studierende",
        "accreditation", "accreditamento", "acreditación",
        "governance", "research", "ricerca", "investigación",
        "recherche"
    ]

    # ⚖️ structural / misconduct / governance signals
    integrity_signals = [
        "misconduct", "fraud", "plagiarism",
        "irregularities", "scandal",
        "scorretta", "mala conducta",
        "fehlverhalten", "fraude",
        "abuse", "violation"
    ]

    keyword_score = sum(1 for k in keyword_signals if k in text)
    integrity_score = sum(1 for k in integrity_signals if k in text)

    # 🧠 combined relevance logic
    # allow either academic context OR integrity signal boost
    return (keyword_score >= 1) or (integrity_score >= 1)

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
