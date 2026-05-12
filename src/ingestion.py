# MAAT ingestion pipeline 
# RSS ingestion + JSONL storage

import feedparser
from datetime import datetime
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from langdetect import detect, DetectorFactory
from urllib.parse import urlparse
import hashlib
from newspaper import Article

DetectorFactory.seed = 0



# 🌍 Multilingual semantic model (lightweight, strong baseline)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

MAAT_CONCEPTS = [
    # general

    "news about universities and higher education",

    # 🏛️ institutional structure

    "university system",

    "higher education institutions",

    "academic organization",

    # ⚖️ governance + policy (core axis)

    "higher education governance",

    "university reform",

    "education policy",

    "funding of universities",

    # 🧠 academic integrity axis

    "academic misconduct",

    "research integrity",

    "scientific fraud",

    "plagiarism in academia",

    # 👥 human/structural dynamics

    "faculty employment",

    "student experience",

    "academic labor",

    "academic labour",

    "research careers",

    # 🌍 system-level change

    "accreditation systems",

    "ranking systems",

    "international universities",

    "higher education crisis"

]

concept_embeddings = model.encode(MAAT_CONCEPTS, convert_to_tensor=True)

RSS_FEEDS = [

    # 🇺🇸 🇬🇧 English (US/UK higher ed focus)
    "https://www.insidehighered.com/rss/news",
    "https://www.timeshighereducation.com/rss",
    "https://www.chronicle.com/rss",
    "https://www.universityworldnews.com/rss.php",
    "https://sciencebusiness.net/rss",
    "https://www.euractiv.com/section/education/rss/",
    "https://wonkhe.com/feed/",
    "https://www.hepi.ac.uk/feed/",
    "https://www.officeforstudents.org.uk/news-and-blog/rss/",
    "https://www.advance-he.ac.uk/news-and-views/rss.xml",
    "https://www.theguardian.com/education/higher-education/rss",
    "https://srheblog.com/feed/",
    "https://www.highereddive.com/feeds/news/",
    "https://www.theguardian.com/education/rss",
    "https://www.bbc.co.uk/news/education/rss.xml",
    "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://www.ft.com/?format=rss",
    "https://www.nature.com/nature.rss",
    "https://www.science.org/rss/news_current.xml",

    # 🇩🇪 German-speaking Europe
    "https://www.forschung-und-lehre.de/rss.xml",
    "https://www.diezeit.de/index.rss",
    "https://www.daad.de/en/the-daad/rss-feed/",
    "https://hochschulforumdigitalisierung.de/feed/",
    "https://www.che.de/rss/",
    "https://www.wissenschaftsrat.de/DE/Home/home_node.html?rss=true",
    "https://www.heise.de/rss/heise-atom.xml",
    "https://www.faz.net/rss/aktuell/gesellschaft/",
    "https://www.bmbf.de/SiteGlobals/Functions/RSSFeed/RSSNewsfeed.xml",
    "https://www.daad.de/en/the-daad/rss-feed/",
    "https://www.mpg.de/rss.xml",

    # 🇫🇷 France
    "https://www.letudiant.fr/rss/actualites.xml",
    "https://www.lemonde.fr/enseignement-superieur/rss_full.xml",
    "https://www.enseignementsup-recherche.gouv.fr/rss.xml",
    "https://www.cnrs.fr/fr/rss.xml",
    "https://www.strategie.gouv.fr/rss.xml",
    "https://www.hceres.fr/en/rss.xml",
    "https://www.campusfrance.org/en/rss.xml",
    "https://www.franceculture.fr/rss",
    "https://www.inrae.fr/rss.xml",
    "https://www.cnrs.fr/fr/rss.xml",
    "https://www.enseignementsup-recherche.gouv.fr/rss.xml",

    # 🇪🇸 Spain
    "https://www.universia.net/rss.xml",
    "https://elpais.com/rss/elpais/educacion.xml",
    "https://www.gob.mx/sep/rss",
    "https://www.argentina.gob.ar/educacion/rss",
    "https://www.mineducacion.gov.co/portal/rss/",
    "https://oei.int/rss",
    "https://www.clacso.org/feed/",
    "https://scielo.org/rss",
    "https://www.csic.es/es/rss.xml",
    "https://www.redalyc.org/rss.xml",
    
    # 🇮🇹 Italy
    "https://www.ilsole24ore.com/rss/economia.xml",
    "https://www.roars.it/feed/",
    "https://www.mur.gov.it/it/rss.xml",
    "https://www.anvur.it/feed/",
    "https://www.cnr.it/rss",
    "https://www.crui.it/rss.xml",
    "https://www.agendadigitale.eu/feed/",
    "https://www.ilpost.it/scienza/feed/",

    # 🇳🇱 Netherlands / EU academia
    "https://www.scienceguide.nl/feed/",
    "https://www.nwo.nl/rss.xml",
    "https://www.vsnu.nl/rss.xml",

    # 🇸🇪 🇩🇰 🇳🇴 Nordic

    "https://www.forskningsradet.no/rss/",
    "https://www.vr.se/english/about-us/news.html/rss",
    "https://ufm.dk/en/news/rss",

    # 🇵🇱 Poland 
    "https://www.gov.pl/web/science/rss",

    # 🇨🇿 Czech Republic (education ministry / academia signals)
    "https://www.msmt.cz/rss",

    # 🇭🇺 Hungary 
    "https://www.kormany.hu/en/rss",

    # 🇷🇴 Romania 
    "https://www.edu.ro/rss.xml",
    "https://acad.ro/rss.xml",

    # 🇧🇬 Bulgaria 
    "https://www.mon.bg/en/rss",
    "https://www.neaa.government.bg/en/rss",

    #🇬🇷 Greece 
    "https://www.minedu.gov.gr/rss",
    "https://www.ethaae.gr/rss",
    "https://www.elidek.gr/rss",

    # 🇿🇦 South Africa 
    "https://www.dhet.gov.za/SitePages/RSS.aspx",

    # 🇮🇳 India 
    "https://www.education.gov.in/en/rss-feeds",

    # 🌍 Global policy / research signals
    "https://www.oecd.org/education/rss.xml",
    "https://www.unesco.org/en/rss-feed",
    "https://www.worldbank.org/en/topic/education/brief/rss",
    "https://www.imf.org/en/News/RSS"
]


RUN_DATE = datetime.utcnow().strftime("%Y-%m-%d")

OUTPUT_FILE = f"data/raw/articles_{RUN_DATE}.jsonl"

def extract_article_text(url):

    try:

        article = Article(url)

        article.download()

        article.parse()

        return article.text.strip()

    except Exception as e:

        log(f"Failed article extraction: {url} | {e}")

        return ""

def load_seen_articles():

    seen = set()

    data_path = Path("data/raw")

    if not data_path.exists():
        return seen

    for file in data_path.glob("articles_*.jsonl"):

        try:
            with open(file, "r", encoding="utf-8") as f:

                for line in f:

                    try:
                        article = json.loads(line)

                        article_id = article.get("article_id")

                        if article_id:
                            seen.add(article_id)

                    except:
                        continue

        except:
            continue

    log(f"Loaded {len(seen)} historical article IDs")

    return seen

def make_article_id(article):

    base = article.get("link", "") or (article.get("title", "") + article.get("published", ""))

    return hashlib.md5(base.encode("utf-8")).hexdigest()

def detect_language(text):
    try:
        return detect(text)
    except:
        return "unknown"

def extract_source_name(url):
    try:
        domain = urlparse(url).netloc
        return domain.replace("www.", "")
    except:
        return url
        
def is_relevant(article):

    text = (article.get("title", "") + " " + article.get("summary", "")).strip()

    if not text:
        return False

    # encode article into vector space
    article_embedding = model.encode(text, convert_to_tensor=True)

    # compute similarity to MAAT conceptual space
    scores = util.cos_sim(article_embedding, concept_embeddings)

    max_score = float(scores.max())

    # threshold (tunable)
    return max_score > 0.45

def log(message):
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")


def fetch_rss_articles(seen):

    articles = []

    for url in RSS_FEEDS:

        log(f"Fetching RSS feed: {url}")

        feed = feedparser.parse(url)

        for entry in feed.entries[:50]:

            text = (entry.get("title", "") + " " + entry.get("summary", "")).strip()

            full_text = extract_article_text(entry.get("link", ""))

            article = {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "full_text": full_text,
                "source": url,
                "journal": extract_source_name(url),
                "language": detect_language(text),
                "run_date": RUN_DATE,
                "retrieved_at": datetime.now().isoformat()
                }

            if not is_relevant(article):
                continue

            article["article_id"] = make_article_id(article)

            if article["article_id"] in seen:

                continue

            seen.add(article["article_id"])
            
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

    seen = load_seen_articles()

    articles = fetch_rss_articles(seen)

    log(f"Collected {len(articles)} articles")

    save_articles_jsonl(articles)

    log("MAAT ingestion complete")


if __name__ == "__main__":
    run_pipeline()
