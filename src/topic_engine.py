import json

from pathlib import Path

from sentence_transformers import SentenceTransformer, util

import numpy as np

from sklearn.cluster import DBSCAN

from sklearn.feature_extraction.text import TfidfVectorizer

from bs4 import BeautifulSoup

import re

import html

from collections import Counter

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

MAAT_TOPICS = {

    "teaching_and_learning": [
        "instructional practice",
        "pedagogical methods",
        "curricular design",
        "course architecture",
        "course evaluation",
        "classroom methods",
        "participatory instruction",
        "competency outcomes",
        "virtual instruction",
        "blended instruction",
        "remote coursework",
        "distance pedagogy",
        "bachelor qualification",
        "STEM qualification",
        "online learning",
        "master qualification",
        "business qualification",
        "doctoral qualification",
        "degree pathway",
        "undergraduate pathway",
        "postgraduate pathway",
        "pedagogical innovation",
        "instructional excellence"
    ],


    "student_experience": [
        "student wellbeing",
        "student life",
        "college experience",
        "supporting staff",
        "student experience",
        "student satisfaction",
        "student engagement",
        "student retention",
        "student protest",
        "student voice",
        "mentor-student relationship"
    ],

    "educational_technology": [
        "artificial intelligence",
        "AI assisted process",
        "generative AI",
        "ChatGPT",
        "emerging technology",
        "digital tools",
        "analytics",
        "edtech",
        "process automation",
        "automated grading",
        "proctoring software",
        "algorithmic assessment"
    ],

    "research_activities": [
        "research collaboration",
        "research productivity",
        "publication pressure",
        "publish or perish",
        "citation count",
        "peer review",
        "open access",
        "h-index",
        "quantitative research",
        "qualitative research",
        "empirical research",
        "theoretical research",
        "high-impact research"
    ],

    "higher_education_crisis": [
        "education crisis",
        "higher education crisis",
        "decline of academia",
        "academic collapse",
        "educational decline",
        "academic model breakdown",
        "educational instability",
        "structural breakdown",
        "unsustainable model",
        "legitimacy crisis",
        "outdated education model",
        "systemic education failure",
    ],

    "education_cost": [
        "tuition fee",
        "debt",
        "loan",
        "tuition affordability",
        "need-based financial support",
        "need-based financial assistance",
        "fee waivers and bursaries",
        "scholarships",
        "cost barriers",
        "cost of attendance support",
        "financial hardship",
    ],
    
   "university_administration": [
       "university bylaws",
       "university leadership",
       "board of trustees",
       "board of regents",
       "university senate",
       "senior leadership",
       "university administrators",
       "organisational structure",
       "university policy",
       "university reform",
       "internal regulations",
       "university reform"
    ],

     "accreditation": [
        "accreditation process",
        "accreditation review",
        "accreditation body",
        "accreditation standards",
        "loss of accreditation",
        "accreditation withdrawal",
        "programme accreditation",
        "institutional accreditation",
        "accreditation compliance",
        "quality assurance review",
        "quality assurance body",
        "external review process",
        "validation process",
]

    "funding_flows": [
        "scholarly funding",
        "public scholarly funding",
        "school budgets",
        "scholarly grant funding",
        "scholarly endowments"
    ],

    "financial_constraints": [
        "austerity",
        "financial concerns",
        "budget cuts",
        "budget constraints",
        "resource constraints",
        "insufficient resources"
    ],

   "faculty_labour": [
        "faculty contracts",
        "adjunct faculty",
        "faculty precarity",
        "faculty labour exploitation",
        "faculty careers",
        "unpaid faculty labour",
        "faculty workload",
        "faculty job insecurity",
        "faculty hiring market",
        "faculty redundancy",
        "faculty unemployment"
    ],

    "academic_standards": [
        "reporting honesty",
        "rigorous standards",
        "reporting clarity",
        "accountable conduct",
        "responsible conduct"
        "integrity",
        "standards of conduct",
        "transparency",
        "accountability",
        "responsibility"
    ],

    "ethical_conflicts": [
        "plagiarism",
        "deliberate misrepresentation",
        "factual misrepresentation",
        "intentional misrepresentation",
        "fraudulent misrepresentation",
        "unethical behaviour",
        "data fabrication",
        "ethical impropriety",
        "data misuse",
        "dishonesty"
    ],

    "norm_violations": [
        "fraud",
        "embezzlement",
        "corruption",
        "bribery",
        "tax evasion",
        "misconduct",
        "insider trading",
        "false declarations",
        "perjury",
        "contempt of court",
        "privacy violation",
        "theft",
        "regulatory violation",
        "compliance breach",
        "unfair contracts"
    ],
        
    "degradation_signals": [
        "grade inflation",
        "declining rigour",
        "credential inflation",
        "content dilution",
        "lower expectations",
        "erosion of rigour",
        "deteriorating outcomes",
        "falling benchmarks",
        "mission erosion",
        "performative commitment",
        "mission drift",
        "oversimplification",
        "dumbing down material",
        "programme massification",
        "over-enrollment",
        "leniency",
        "rubric inflation",
        "benchmark drift",
        "skills mismatch",
        "employability gap",
        "opportunistic growth",
        "incompetence",
        "credential depreciation"
    ],

     "academic abuse": [
         "administrative coercion",
         "procedural abuse",
         "retaliation",
         "institutional abuse",
         "retaliatory litigation",
         "suppressing dissent",
         "silencing criticism",
         "risks attached to reporting abuse",
         "fear-driven self-silencing",
         "wrongful termination",
         "professional marginalisation",
         "career sabotage",
         "procedural manipulation",
         "bureaucratic obstruction",
         "disproportionate punishment",
         "exclusion",
         "promotion blockage",
         "arbitrary tenure denial",
         "arbitrary disciplinary actions",
         "institutional gatekeeping",
         "reputation damage tactics",
         "non-transparent procedures",
         "mobbing",
         "scarcity-based exploitation",
         "weaponised hierarchy",
         "weaponised collegiality"
    ],

     "accountability_gaps": [
         "nepotism",
         "cover-up",
         "conflict of interest",
         "weak oversight",
         "power asymetry",
         "power consolidation",
         "elite impunity",
         "lack of oversight",
         "unchecked authority",
         "decision-making opacity",
         "informal power networks",
         "self-regulation",
         "abuse of office"
    ],

    
    "systemic_inequity": [
        "discrimination",
        "title IX",
        "racism",
        "bullying",
        "diversity equity and inclusion initiatives",
        "equity initiatives",
        "gender discrimination",
        "sexual harassment",
        "workplace harassment",
        "workplace ubias",
        "inclusivity",
        "accessibility equity",
        "hate incidents",
        "biased systems",
        "toxic culture",
        "harmful culture",
        "hostile culture",
        "corrosive culture"
    ],

    "ranking_systems": [
        "rankings",
        "benchmarking",
        "target metrics",
        "performance metrics",
        "performance indicators"
    ],

    "politics": [
        "geopolitics",
        "foreign affairs",
        "authoritarianism",
        "democracy",
        "illiberal democracy",
        "fascism",
        "nationalism",
        "populism",
        "legislation",
        "sovereignty",
        "territorial dispute",
        "war",
        "armed dispute",
        "proxy war",
        "civil war",
        "military escalation",
        "deterrence",
        "nuclear strategy",
        "sanctions",
        "economic warfare",
        "trade war",
        "diplomacy",
        "summits",
        "alliances",
        "NATO",
        "UN",
        "civil unrest",
        "instability",
        "uprising",
        "regime",
        "political repression",
        "political interference",
        "state surveillance",
        "propaganda"
    ],

    "regions_and_countries": [
        "north america",
        "latin america",
        "south america",
        "europe",
        "western europe",
        "eastern europe",
        "asia",
        "east asia",
        "south asia",
        "southeast asia",
        "middle east",
        "central asia",
        "africa",
        "north africa",
        "sub-saharan africa",
        "oceania",
        "united states of america",
        "canada",
        "mexico",
        "brazil",
        "argentina",
        "european union",
        "russia",
        "china",
        "india",
        "japan",
        "south korea",
        "iran",
        "turkey",
        "israel",
        "palestine",
        "gaza strip",
        "ukraine",
        "united kingdom",
        "france",
        "germany",
        "italy",
        "spain",
        "australia",
        "indonesia",
        "nigeria",
        "south africa",
        "egypt"
    ],

    "internationalisation": [
        "international cohorts",
        "international exchange",
        "international mobility",
        "study abroad",
        "visa restrictions",
        "global experience",
        "cross-border experience",
        "international partnerships",
        "transnational mobility",
        "brain drain"
    ],

    "admissions_access": [
        "admissions criteria",
        "admissions selectivity",
        "standardised testing",
        "scholastic aptitude test",
        "graduate record examination",
        "graduate management admission test",
        "affirmative action",
        "widening participation"
    ],

    "campus_infrastructure": [
        "accommodation",
        "safety",
        "laboratories",
        "facilities",
        "library services",
        "infrastructure"
    ],

    "academic_freedom": [
        "freedom of expression",
        "freedom of speech",
        "freedom of opinion",
        "censorship",
        "hierarchical interference",
        "intellectual autonomy",
        "thought independence"
    ],

    "sustainability_climate": [
        "climate change",
        "sustainability",
        "green campus",
        "environmental sustainability",
        "carbon neutrality",
        "fossil fuel",
    ],

    "health_professions": [
        "medical profession",
        "nursing profession",
        "health profession",
        "clinical training",
        "training hospitals"
    ],

    "science_society": [
        "public misinformation",
        "media falsehoods",
        "false narratives",
        "fabricated news",
        "contested scientific claims"
        "trust in science",
        "science communication",
        "evidence-based reasoning",
        "politicisation of science",
        "scientific expertise"    
    ],
    
    "future_outlook": [
        "pessimism",
        "optimism",
        "uncertainty",
        "anxiety",
        "future planning",
        "morale"
    ]
}

def flatten_topics(topic_dict):
    return [
        item
        for sublist in topic_dict.values()
        for item in sublist
    ]
    
CLUSTER_NAMES = list(MAAT_TOPICS.keys())
FLAT_MAAT_TOPICS = flatten_topics(MAAT_TOPICS)
topic_embeddings = model.encode(FLAT_MAAT_TOPICS, convert_to_tensor=True)

def build_topic_to_cluster_map(MAAT_TOPICS):
    mapping = {}

    for cluster, topics in MAAT_TOPICS.items():
        for t in topics:
            mapping[t] = cluster

    return mapping

def extract_phrases(article):
    text = build_semantic_text(article)

    if len(text.split()) < 30:
        return []

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=8,
        ngram_range=(2,3)
    )

    try:
        X = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out()
    except:
        return []

def is_valid_topic(phrase, maat_embeddings, model, threshold=0.30):
    emb = model.encode(phrase, convert_to_tensor=True)

    sims = util.cos_sim(emb, maat_embeddings)[0].cpu().numpy()

    return float(np.max(sims)) >= threshold

def clean_text(text):
    if not text:
        return ""

    soup = BeautifulSoup(text, "lxml")
    cleaned = soup.get_text(separator=" ")

    cleaned = re.sub(r"http\S+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()

def filter_topics(phrases):
    cleaned = []

    for p in phrases:
        p = p.strip().lower()

        # remove 1-word garbage
        if len(p.split()) == 1 and p in DOMAIN_STOPWORDS:
            continue

        # remove pure boilerplate words
        if p in DOMAIN_STOPWORDS:
            continue

        # remove very short tokens
        if len(p) < 4:
            continue

        # remove numeric / junk
        if re.fullmatch(r"[a-z]{1,2}", p):
            continue

        cleaned.append(p)

    return cleaned

def build_matrix(articles, embeddings, topics, model, topic_to_cluster):

    topic_embeddings = model.encode(topics, convert_to_tensor=True)

    matrix = []

    for i, article in enumerate(articles):

        scores = util.cos_sim(
            embeddings[i],
            topic_embeddings
        )[0].cpu().numpy()

        matrix.append({
            "article_id": article.get("article_id"),
            "title": article.get("title"),
            "link": article.get("link"),
            "scores": [
                {
                    "topic": topics[j],
                    "cluster": topic_to_cluster.get(topics[j], "unknown"),
                    "score": float(scores[j])
                }
                for j in range(len(topics))
            ]
        })

    return matrix



def resolve_topics(maat_topics, discovered_topics, model, threshold=0.82):
    """
    Returns:
    - all_topics (deduplicated)
    - overlap_mapping
    """

    overlap_mapping = []
    final_topics = list(maat_topics)

    maat_embeddings = model.encode(maat_topics, convert_to_tensor=True)

    for dt in discovered_topics:
        dt_emb = model.encode(dt, convert_to_tensor=True)

        sims = util.cos_sim(dt_emb, maat_embeddings)[0].cpu().numpy()

        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])

        if best_score >= threshold:
            # OVERLAP → keep MAAT name
            overlap_mapping.append({
                "discovered": dt,
                "matched_to": maat_topics[best_idx],
                "score": round(best_score, 4)
            })

        else:
            final_topics.append(dt)

    return final_topics, overlap_mapping

def build_semantic_text(article):

    body = (

        article.get("translated_text")

        if article.get("translated_text")

        else article.get("full_text", "")

    )

    semantic_text = " ".join([

        clean_text(article.get("title", "")),

        clean_text(article.get("summary", "")),

        clean_text(body)

    ])

    return semantic_text.strip()




def load_articles(path):

    data = []

    with open(path, "r", encoding="utf-8") as f:

        for line in f:

            try:

                data.append(json.loads(line))

            except:

                pass

    return data


def embed_articles(articles):

    texts = [

        build_semantic_text(a)

        for a in articles

    ]

    return model.encode(texts)


def extract_candidate_topics(
    articles,
    model,
    maat_topics,
    max_features=10,
    phrase_sim_threshold=0.30,
    dedup_threshold=0.85
):

    candidate_phrases = []
    final_topics = []

    maat_embeddings = model.encode(maat_topics, convert_to_tensor=True)

    # ----------------------------
    # STEP 1: extract phrases
    # ----------------------------
    for article in articles:

        text = build_semantic_text(article)

        if len(text.split()) < 40:
            continue

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=max_features,
                ngram_range=(2, 3)
            )

            vectorizer.fit_transform([text])
            phrases = vectorizer.get_feature_names_out()

            phrases = filter_topics(phrases)

            for p in phrases:
                p = p.strip().lower()

                if len(p) < 4:
                    continue

                if any(x in p for x in ["cookie", "subscribe", "user", "accept"]):
                    continue

                # -----------------------------------
                # 🧠 SEMANTIC EDUCATION GATE (CRITICAL)
                # -----------------------------------
                emb = model.encode(p, convert_to_tensor=True)

                sims = util.cos_sim(emb, maat_embeddings)[0].cpu().numpy()
                best_sim = float(np.max(sims))

                if best_sim < phrase_sim_threshold:
                    continue  # reject non-education-space phrases

                candidate_phrases.append(p)

        except:
            continue

    # ----------------------------
    # STEP 2: semantic filter vs MAAT space
    # ----------------------------
    phrase_embeddings = model.encode(candidate_phrases, convert_to_tensor=True)

    filtered = []

    for i, phrase in enumerate(candidate_phrases):

        sims = util.cos_sim(
            phrase_embeddings[i],
            maat_embeddings
        )[0].cpu().numpy()

        max_sim = float(np.max(sims))

        # THIS is the key gate:
        # must belong to education / academic discourse space
        if max_sim >= phrase_sim_threshold:
            filtered.append((phrase, phrase_embeddings[i]))

    if not filtered:
        return []

    # ----------------------------
    # STEP 3: deduplicate in embedding space
    # ----------------------------
    unique = []

    for phrase, emb in filtered:

        keep = True

        for existing in unique:
            sim = util.cos_sim(emb, existing["emb"]).item()

            if sim >= dedup_threshold:
                keep = False
                break

        if keep:
            unique.append({
                "topic": phrase,
                "emb": emb
            })

    return [x["topic"] for x in unique]



# RUN

def run():

    path = sorted(Path("data/raw").glob("articles_*.jsonl"))[-1]
    date_str = path.stem.replace("articles_", "")

    print(f"Processing date: {date_str}")

    articles = load_articles(path)
    embeddings = embed_articles(articles)

    discovered = extract_candidate_topics(

    articles,

    model,

    FLAT_MAAT_TOPICS

    )

    all_topics, overlap = resolve_topics(
        FLAT_MAAT_TOPICS,
        discovered,
        model
    )

    topic_to_cluster = build_topic_to_cluster_map(MAAT_TOPICS)

    matrix = build_matrix(
        articles,
        embeddings,
        all_topics,
        model,
        topic_to_cluster
    )

    Path("data/topics").mkdir(
    parents=True,
    exist_ok=True
    )

    with open(
        f"data/topics/topic_matrix_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(matrix, f, indent=2, ensure_ascii=False)

    with open(
        f"data/topics/overlap_topics_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(overlap, f, indent=2, ensure_ascii=False)

    with open(
        f"data/topics/all_topics_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(all_topics, f, indent=2, ensure_ascii=False)

    print("MAAT TOPIC ENGINE COMPLETE")

if __name__ == "__main__":

    run()

