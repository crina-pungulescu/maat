# MAAT ingestion pipeline 
# RSS ingestion + JSONL storage

import requests
import feedparser
from datetime import datetime
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from langdetect import detect, DetectorFactory
from urllib.parse import urlparse
import hashlib
from newspaper import Article
from transformers import pipeline
from deep_translator import GoogleTranslator
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


DetectorFactory.seed = 0


# 🌍 Multilingual semantic model (lightweight, strong baseline)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

from topic_engine import MAAT_TOPICS

MAAT_CATEGORY_LABELS = list(MAAT_TOPICS.keys())

concept_embeddings = model.encode(MAAT_CATEGORY_LABELS, convert_to_tensor=True)

model_name = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(model_name)
# summarization_model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

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
    "https://www.theguardian.com/education/rss",
    "https://www.bbc.co.uk/news/education/rss.xml",
    "https://www.edweek.org/feeds/all.rss",
    "https://hechingerreport.org/feed/",
    "https://www.chalkbeat.org/feeds/all/rss.xml",
    "https://www.edsurge.com/articles.rss",
    "https://www.aaup.org/news/feed",
    "https://www.aaup.org/rss.xml",
    "https://www.aaup.org/reports-publications/rss.xml",
    "https://www.facultyforward.org/rss.xml",
    "https://www.academicfreedom.org/feed/",
    "https://www.insidehighered.com/rss/views",
    "https://www.insidehighered.com/rss/quicktakes",
    "https://www.timeshighereducation.com/opinion/rss",
    "https://www.nature.com/subjects/higher-education.rss",
    "https://www.nsf.gov/news/newsrss.xml",
    "https://new.nsf.gov/rss/news_all.xml",
    "https://www.nih.gov/news-events/news-releases/feed",
    "https://www.ed.gov/feed",
    "https://www.ed.gov/news/press-releases/feed",
    "https://ies.ed.gov/newsfeed/rss.asp",
    "https://nces.ed.gov/whatsnew/rss.xml",
    "https://www.grants.gov/rss/GG_NewOpps.xml",
    "https://www.oecd.org/education/rss.xml",
    "https://www.worldbank.org/en/topic/education/rss",
    "https://www.unesco.org/en/rss.xml",
    "https://www.eua.eu/news/rss.xml",
    "https://www.eua.eu/news/eua-news.rss",
    "https://www.eua.eu/news/eua-publications.rss",
    "https://www.universityworldnews.com/rss.php?format=rss",
    "https://www.thefire.org/news/feed/",
    "https://www.thefire.org/rss/",
    "https://www.aaup.org/issues/academic-freedom/feed",
    "https://www.aaup.org/issues/governance/feed",
    "https://www.aaup.org/issues/tenure/feed",
    "https://www.chronicle.com/section/Opinion/rss",
    "https://www.chronicle.com/section/Advice/rss",
    "https://www.insidehighered.com/rss/careers",
    "https://www.insidehighered.com/rss/tenure-track",
    "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://www.reuters.com/rssFeed",
    "https://apnews.com/hub/rss",
    "https://news.google.com/rss/search?q=students",
    "https://news.google.com/rss/search?q=academia",
    "https://news.google.com/rss/search?q=education",
    "https://news.google.com/rss/search?q=academic+standards",
    "https://news.google.com/rss/search?q=campus",
    "https://news.google.com/rss/search?q=academic+misconduct",
    "https://news.google.com/rss/search?q=tenure-track",
    "https://news.google.com/rss/search?q=college",
    "https://news.google.com/rss/search?q=higher+education",
    "https://news.google.com/rss/search?q=university",
    "https://news.google.com/rss/search?q=universities",
    "https://news.google.com/rss/search?q=academic+research",
    "https://news.google.com/rss/search?q=faculty",
    "https://news.google.com/rss/search?q=professor",
    "https://news.google.com/rss/search?q=college+administration",
    "https://news.google.com/rss/search?q=research+university",
    "https://news.google.com/rss/search?q=academic+freedom",
    "https://news.google.com/rss/search?q=tenure",
    "https://news.google.com/rss/search?q=adjunct+faculty",
    "https://news.google.com/rss/search?q=graduate+students",
    "https://news.google.com/rss/search?q=doctoral+students",
    "https://news.google.com/rss/search?q=research+integrity",
    "https://news.google.com/rss/search?q=plagiarism+university",
    "https://news.google.com/rss/search?q=Title+IX+university",
    "https://news.google.com/rss/search?q=university+funding",
    "https://news.google.com/rss/search?q=academic+labor",
    "https://news.google.com/rss/search?q=student+debt+university",
    "https://news.google.com/rss/search?q=research+funding",
    "https://news.google.com/rss/search?q=university+rankings",
    "https://news.google.com/rss/search?q=higher+education+policy",
    "https://news.google.com/rss/search?q=university+governance",
    "https://news.google.com/rss/search?q=higher+education+crisis",
    "https://news.google.com/rss/search?q=college+meltdown",
    "https://news.google.com/rss/search?q=politicised+academia",
    "https://news.google.com/rss/search?q=teaching+learning+university",
    "https://news.google.com/rss/search?q=student+experience",
    "https://news.google.com/rss/search?q=university+governance",
    "https://news.google.com/rss/search?q=higher+education+cost",
    "https://news.google.com/rss/search?q=university+administration",
    "https://news.google.com/rss/search?q=university+board+trustees",
    "https://news.google.com/rss/search?q=university+board+regents",
    "https://news.google.com/rss/search?q=university+accreditation",
    "https://news.google.com/rss/search?q=university+msche",
    "https://news.google.com/rss/search?q=university+aacsb",
    "https://news.google.com/rss/search?q=university+budget",
    "https://news.google.com/rss/search?q=faculty+precarity",
    "https://news.google.com/rss/search?q=academic+standards",
    "https://news.google.com/rss/search?q=ethics+academia",
    "https://news.google.com/rss/search?q=academic+abuse",
    "https://news.google.com/rss/search?q=accountability+academia",
    "https://news.google.com/rss/search?q=transparency+academia",
    "https://news.google.com/rss/search?q=university+oversight",
    "https://news.google.com/rss/search?q=study+abroad",
    "https://news.google.com/rss/search?q=university+governance",
    "https://news.google.com/rss/search?q=academic+freedom",
    "https://news.google.com/rss/search?q=future+academia",
    "https://www.reuters.com/world/rss",
    "https://www.reuters.com/rssFeed/topNews",
    "https://apnews.com/hub/ap-top-news?output=rss",
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/international/rss",
    "https://feeds.washingtonpost.com/rss/national",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://rssfeeds.usatoday.com/usatoday-NewsTopStories",
    "https://www.independent.co.uk/rss",
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "http://rss.cnn.com/rss/cnn_world.rss",
    "https://www.nbcnews.com/rss-feeds",
    "https://abcnews.go.com/abcnews/topstories",
    "https://www.cbsnews.com/latest/rss/main",
    "https://feeds.npr.org/1001/rss.xml",
    "https://www.pbs.org/newshour/feeds/rss/headlines",
    "https://www.cbc.ca/cmlink/rss-topstories",
    "https://feeds.skynews.com/feeds/rss/home.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://theconversation.com/global/articles.atom",
    "https://www.worldpoliticsreview.com/feed",
    "https://www.foreignaffairs.com/rss.xml",
    "https://www.euronews.com/rss?format=mrss",
    "https://www.france24.com/en/rss",
    "https://www.rte.ie/news/rss/news-headlines.xml",
    "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "https://www.scmp.com/rss/91/feed",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://www.thehindu.com/news/feeder/default.rss",
    "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.ft.com/markets?format=rss",
    "https://thepienews.com/feed/",
    "https://www.facultyfocus.com/feed/",
    "https://www.ruffalonl.com/blog/feed/",
    "https://tophat.com/feed/",
    "https://www.insidehighered.com/rss.xml",
    "https://feeds.feedburner.com/EdTechHiEd",
    "https://www.advance-he.ac.uk/news-and-views/feed",
    "https://www.educationdynamics.com/feed/",
    "https://www.terminalfour.com/blog/rss/index.xml",
    "https://wonkhe.com/feed/",
    "https://feeds.feedburner.com/mfeldstein/feed",
    "https://www.hepi.ac.uk/category/blog/feed/",
    "https://www.higheredtoday.org/feed/",
    "https://www.campusreview.com.au/feed/",
    "https://feeds.feedburner.com/OnlineContinuingProfessionalEducationUpdateByUpcea",
    "https://www.scholarlyteacher.com/blog-feed.xml",
    "https://www.highereducationinquirer.org/feeds/posts/default",
    "https://www.higheredgeek.com/blog?format=RSS",
    "https://feeds.feedburner.com/highereducationwhisperer",
    "https://srheblog.com/feed/",
    "https://teachinginhighered.com/feed/",
    "https://edualliancegroup.blog/feed/",
    "https://sovorelpublishing.com/index.php/feed/",
    "https://www.continuous-learning-institute.com/blog.rss",
    "https://www.theguardian.com/education/higher-education/rss",
    "https://wenr.wes.org/feed/",
    "https://higheredstrategy.com/blog/feed/",
    "highereddatastories.com/feeds/posts/default",
    "https://recessionreality.blogspot.com/feeds/posts/default",
    "https://andrewmcgettigan.org/feed/",
    "https://ihec-djc.blogspot.com/feeds/posts/default",
    "https://www.feedspot.com/infiniterss.php?_src=feed_title&followfeedid=4654987&q=site:https%3A%2F%2Fteachingandlearninginhighered.org%2Ffeed%2F",
    "https://higheredincrisis.org/feed/",
    "https://feeds.feedburner.com/Inside-Higher-Ed",
    "https://aeradivisionj.blogspot.com/feeds/posts/default?alt=rss",
    "https://www.millennialprofessor.com/feeds/posts/default?alt=rss",
    "https://mistakengoal.com/blog/feed/",
    "https://feeds.feedburner.com/highedwebtech",
    "https://globalhighered.wordpress.com/feed/",
    "https://helpfulprofessor.com/feed/",
    "https://www.timeshighereducation.com/academic/blog",
    
    

    # 🇩🇪 German-speaking Europe
    "https://www.forschung-und-lehre.de/rss.xml",
    "https://rss.dw.com/rdf/rss-en-all",
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
    "https://studyindenmark.dk/news/aggregator/RSS",

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
SEEN_FILE = Path("data/raw/seen_articles.json")

def clean_jsonl_file(filepath):

    cleaned_lines = []

    removed = 0

    with open(filepath, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            # skip truly empty lines
            if not line:
                removed += 1
                continue

            try:

                article = json.loads(line)

            except Exception:

                removed += 1
                continue

            # remove malformed / incomplete articles
            if not validate_final(article):
                removed += 1
                continue

            if not is_valid_article(article):
                removed += 1
                continue

            cleaned_lines.append(
                json.dumps(article, ensure_ascii=False)
            )

    # rewrite cleaned file
    with open(filepath, "w", encoding="utf-8") as f:

        for line in cleaned_lines:
            f.write(line + "\n")

    log(f"Cleaned JSONL file: removed {removed} bad rows")

def generate_summary(text):

    if not text:
        return ""

    try:
        prompt = "Summarize in English:\n\n" + text

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

        outputs = summarization_model.generate(
            **inputs,
            max_new_tokens=500
        )

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    except Exception as e:
        log(f"Summary failed: {e}")
        return ""

def translate_to_english(text):

    if not text:

        return ""

    try:

        return GoogleTranslator(source='auto', target='en').translate(text)

    except Exception as e:

        log(f"Translation failed: {e}")

        return text


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

    if not SEEN_FILE.exists():

        log("No seen_articles.json found. Creating new memory set.")

        return set()

    try:

        with open(SEEN_FILE, "r", encoding="utf-8") as f:

            seen = set(json.load(f))

        log(f"Loaded {len(seen)} seen article IDs")

        return seen

    except Exception as e:

        log(f"Failed loading seen articles: {e}")

        return set()

def save_seen_articles(seen):

    try:

        SEEN_FILE.parent.mkdir(parents=True, exist_ok=True)

        with open(SEEN_FILE, "w", encoding="utf-8") as f:

            json.dump(sorted(list(seen)), f, indent=2)

        log(f"Saved {len(seen)} seen article IDs")

    except Exception as e:

        log(f"Failed saving seen articles: {e}")

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
        
def compute_relevance(text):
    if not text:
        return False, 0.0

    article_embedding = model.encode(text, convert_to_tensor=True)
    scores = util.cos_sim(article_embedding, concept_embeddings)

    max_score = float(scores.max())
    return max_score > 0.45, max_score

def log(message):
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {message}")

def normalize_title(title: str) -> str:

    return " ".join(title.lower().strip().split())

required = ["article_id", "title", "link", "full_text"]

def validate_final(article):

    return article and all(article.get(k) for k in required)

def is_valid_article(article: dict) -> bool:
    """
    Final safety gate: prevents empty or malformed rows from entering dataset.
    """

    required_fields = ["title", "link", "full_text", "article_id"]

    # 1. missing fields
    for f in required_fields:
        if not article.get(f):
            return False

    # 2. empty / whitespace-only fields
    if not article["title"].strip():
        return False

    if not article["full_text"].strip():
        return False

    # 3. minimum content sanity
    if len(article["full_text"]) < 1500:
        return False

    # 4. link sanity
    if not article["link"].startswith("http"):
        return False

    return True

def fetch_rss_articles(seen):

    seen_titles = set()

    articles = []

    for url in RSS_FEEDS:

        log(f"Fetching RSS feed: {url}")

        try:

            response = requests.get(

            url,

            timeout=10,

            headers={

                "User-Agent": "Mozilla/5.0"

                }

            )

            response.raise_for_status()

            feed = feedparser.parse(response.content)

        except Exception as e:

            log(f"RSS fetch failed: {url} | {e}")

            continue

        for entry in feed.entries[:25]:

            text = (entry.get("title", "") + " " + entry.get("summary", "")).strip()

            full_text = extract_article_text(entry.get("link", ""))

            title_norm = normalize_title(entry.get("title", ""))

            if title_norm in seen_titles:

                continue

            seen_titles.add(title_norm)

            if not full_text or len(full_text) < 1000:
                continue

            is_rel, max_score = compute_relevance(text)

            if not is_rel:
                continue
                
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
                "retrieved_at": datetime.now().isoformat(),
                "relevance_score": max_score
                }

            article["article_id"] = make_article_id(article)

            if article["article_id"] in seen:

                continue

            seen.add(article["article_id"])

            if article["language"] != "en":

                article["translated_text"] = translate_to_english(full_text)

            else:

                article["translated_text"] = ''

            if not validate_final(article) or not is_valid_article(article):

                continue
            
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

    clean_jsonl_file(OUTPUT_FILE)

    save_seen_articles(seen)

    log("MAAT ingestion complete")


if __name__ == "__main__":
    run_pipeline()
