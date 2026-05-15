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

    "teaching_learning": [
        "teaching",
        "learning",
        "pedagogy",
        "instruction",
        "curriculum",
        "classroom",
        "syllabus",
        "course design",
        "student engagement",
        "assessment",
        "educational practice",
        "active learning",
        "learning outcomes",
        "online learning",
        "hybrid learning",
        "distance education",
        "remote teaching",
        "higher education teaching"
    ],


    "student_experience": [
        "student wellbeing",
        "student mental health",
        "student life",
        "student support",
        "student satisfaction",
        "student engagement",
        "student participation",
        "student retention",
        "campus climate",
        "student belonging",
        "student protest",
        "student voice",
        "student-faculty relations",
        "teacher-student relationship"
    ],

    "educational_technology": [
        "artificial intelligence",
        "AI in education",
        "generative AI",
        "ChatGPT",
        "educational technology",
        "digital learning",
        "learning analytics",
        "edtech",
        "automation in education",
        "automated grading",
        "AI-assisted learning",
        "AI-assisted teaching",
        "surveillance technology",
        "proctoring software",
        "algorithmic assessment"
    ],

    "research_activities": [
        "scientific collaboration",
        "research productivity",
        "publication pressure",
        "publish or perish",
        "citation metrics",
        "peer review",
        "research evaluation",
        "academic publishing",
        "open access",
        "scientific innovation"
    ],

    "higher_education_crisis": [
        "institutional crisis",
        "education crisis",
        "university crisis",
        "systemic crisis",
        "institutional crisis",
        "decline of academia",
        "academic collapse",
        "university decline",
        "erosion of higher education",
        "breakdown of academic systems",
        "crisis in universities",
        "collapse of standards",
        "educational instability",
        "structural breakdown",
        "unsustainable higher education model",
        "crisis of legitimacy",
        "crisis narrative",
        "institutional strain",
        "systemic failure framing",
        "post-secondary education crisis"
    ],

    "education_cost": [
        "student debt",
        "tuition",
        "financial aid",
        "scholarships",
        "affordability of education",
        "student poverty",
        "access to higher education",
        "educational inequality"
    ],
    
   "university_administration": [
        "governance",
        "regulation",
        "accreditation",
        "higher education governance",
        "institutional structure"
    ],

    "policy_dynamics": [
        "policy",
        "reform",
        "education policy",
        "higher education reform",
        "policy change",
        "legislative reform"
    ],

    "governance_failure": [
        "bureaucracy",
        "institutional opacity",
        "regulatory capture",
        "governance failure",
        "procedural abuse",
        "overregulation"
    ],

    "funding_flows": [
        "funding",
        "research funding",
        "public funding",
        "university budgets",
        "grants",
        "endowments",
    ],

    "financial_constraints": [
        "austerity",
        "budget cuts",
        "resource constraints",
        "financial pressure in academia",
        "underfunding",
        "cost cutting"
    ],

   "academic_labour": [
        "employment",
        "faculty contracts",
        "adjuncts",
        "precarity",
        "academic careers",
        "unpaid labour",
        "labour exploitation in academia",
        "academic workload",
        "job insecurity",
        "graduate employment",
        "exploitation",
        "academic exploitation",
        "labour exploitation",
        "systemic inequality",
        "redundancy",
        "career",
        "unemployment"
    ],

    "academic_standards": [
        "integrity",
        "ethics",
        "transparency",
        "accountability",
        "DEI",
        "quality of education",
        "responsibility"
    ],

    "ethical_conflict": [
        "plagiarism",
        "research misconduct",
        "misrepresentation",
        "data fabrication",
        "conflict of interest",
        "ethical breach",
        "academic dishonesty"
    ],

    "legal_violations": [
        "fraud",
        "embezzlement",
        "corruption",
        "financial misconduct",
        "bribery",
        "money laundering",
        "tax evasion",
        "financial misconduct",
        "insider trading",
        "market manipulation",
        "accounting fraud",
        "false reporting",
        "perjury",
        "obstruction of justice",
        "contempt of court",
        "illegal surveillance",
        "data privacy violation",
        "cybercrime",
        "intellectual property theft",
        "academic fraud",
        "research misconduct",
        "regulatory violation",
        "compliance breach",
        "contract fraud",
        "consumer fraud",
        "corporate crime"
    ],
        
    "degradation_signals": [
        "grade inflation",
        "declining standards",
        "credential inflation",
        "academic dilution",
        "lowered assessment rigor",
        "reduced academic expectations",
        "quality erosion",
        "institutional decline",
        "loss of rigor",
        "curriculum simplification",
        "dumbing down of education",
        "massification of higher education",
        "over-enrollment pressure",
        "performance compression",
        "assessment leniency",
        "rubric inflation",
        "benchmark drift",
        "skills mismatch",
        "employability gap",
        "credential devaluation"
    ],

     "academic abuse": [
         "administrative coercion",
         "power asymmetry",
         "retaliation",
         "workplace abuse",
         "institutional abuse",
         "retaliatory litigation",
         "silencing dissent",
         "suppression of faculty dissent",
         "risks attached to reporting abuse",
         "chilling effects",
         "self-censorship",
         "wrongful termination",
         "academic retaliation",
         "professional marginalization",
         "career sabotage",
         "hostile work environment",
         "procedural manipulation",
         "bureaucratic obstruction",
         "informal punishment",
         "exclusion from decision making",
         "grant interference",
         "promotion blockage",
         "tenure denial pressure",
         "peer review weaponization",
         "disciplinary misuse",
         "institutional gatekeeping",
         "reputation damage tactics",
         "non-transparent evaluation processes",
         "mobbing"
    ],

     "accountability_gaps": [
         "lack of accountability for powerful actors",
         "nepotism",
         "institutional protection",
         "conflict of interest",
         "power consolidation",
         "elite impunity",
         "lack of oversight",
         "weak governance",
         "regulatory capture",
         "institutional shielding",
         "absence of transparency",
         "unchecked authority",
         "decision-making opacity",
         "informal power networks",
         "career protection for senior figures",
         "failure of internal review processes",
         "self-regulation failure",
         "disciplinary inaction"
    ],

    "inequality_structures": [
        "exploitation",
        "scarcity systems producing exploitation",
        "hierarchy distorting fairness",
        "structural pressure enabling abuse",
        "institutional hierarchy",
        "unequal power distribution",
        "stratified academic systems",
        "competitive funding systems",
        "zero-sum resource allocation"
    ],

    "equity_social_issues": [
        "discrimination",
        "title IX",
        "racism",
        "bullying",
        "harassment",
        "DEI",
        "equity initiatives",
        "gender discrimination",
        "racial discrimination",
        "sexual harassment",
        "workplace harassment",
        "institutional bias",
        "systemic inequality",
        "inclusive policy frameworks",
        "accessibility equity",
        "protected class discrimination",
        "hate incidents",
        "bias reporting systems",
        "campus climate"
    ],

    "ranking_systems": [
        "university rankings",
        "global university rankings",
        "institutional benchmarking",
        "higher education systems",
        "university evaluation metrics",
        "performance indicators in education",
        "system-level comparison",
        "higher education governance structures"
    ],

    "geopolitics": [
        "politics",
        "international relations",
        "foreign policy",
        "geopolitics",
        "authoritarianism",
        "democracy",
        "illiberal democracy",
        "fascism",
        "nationalism",
        "populism",
        "state power",
        "sovereignty",
        "territorial conflict",
        "war",
        "armed conflict",
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
        "United Nations",
        "protest",
        "civil unrest",
        "revolution",
        "uprising",
        "regime change",
        "political repression",
        "state surveillance",
        "propaganda"
    ],

    "regions_countries": [
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
        "united states",
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
        "gaza",
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
        "international students",
        "student mobility",
        "academic mobility",
        "study abroad",
        "visa restrictions",
        "global education",
        "cross-border education",
        "international partnerships",
        "transnational education",
        "international higher education",
        "global higher education landscape",
        "cross-border education systems",
        "brain drain"
    ],

    "admissions_access": [
        "college admissions",
        "university admissions",
        "admissions policy",
        "selective admissions",
        "standardized testing",
        "SAT",
        "affirmative action",
        "access to university",
        "educational access",
        "widening participation"
    ],

    "campus_infrastructure": [
        "campus housing",
        "student accommodation",
        "university campus",
        "campus safety",
        "laboratories",
        "research facilities",
        "library services",
        "digital infrastructure",
        "campus expansion"
    ],

    "academic_freedom": [
        "academic freedom",
        "freedom of expression",
        "campus speech",
        "faculty speech",
        "censorship",
        "political interference",
        "scholarly autonomy",
        "institutional independence"
    ],

    "sustainability_climate": [
        "climate change",
        "sustainability",
        "green campus",
        "environmental policy",
        "climate education",
        "carbon neutrality",
        "fossil fuel",
        "sustainable university"
    ],

    "health_professions_education": [
        "medical education",
        "nursing education",
        "public health education",
        "clinical training",
        "medical students",
        "teaching hospitals"
    ],

    "science_society": [
        "public trust in science",
        "science communication",
        "misinformation",
        "evidence-based policy",
        "politicization of science",
        "scientific expertise"    
    ],
    
    "sentiment_outlook": [
        "future",
        "pessimism",
        "optimism",
        "academic uncertainty",
        "institutional anxiety",
        "future of higher education",
        "educational pessimism",
        "academic morale"
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

