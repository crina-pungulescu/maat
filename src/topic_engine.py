import json

from pathlib import Path

from sentence_transformers import SentenceTransformer, util

import numpy as np

from sklearn.cluster import DBSCAN

from sklearn.feature_extraction.text import TfidfVectorizer

from bs4 import BeautifulSoup

import re

import html

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

MAAT_TOPICS = {
    
   "institutional_structure": [
        "governance",
        "regulation",
        "accreditation",
        "higher education governance",
        "university administration"
    ],

    "policy_dynamics": [
        "policy",
        "reform",
        "education policy",
        "higher education reform",
        "policy change",
        "legislative reform"
    ],

    "governance_pathology": [
        "bureaucracy",
        "administrative coercion",
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
        "unemployment"
    ],

    "academic_standards": [
        "integrity",
        "ethics",
        "transparency",
        "accountability",
        "DEI",
        "responsibility"
    ],

    "norm_violations": [
        "fraud",
        "plagiarism",
        "embezzelment",
        "academic fraud",
        "research misconduct",
        "jeffrey epstein",
        "donald trump"
    ],
        
    "degradation_signals": [
        "grade inflation",
        "declining standards",
        "credential inflation"
    ],

     "coercion_and_abuse": [
        "academic abuse",
        "power asymmetry",
        "retaliation",
        "workplace abuse",
        "institutional abuse",
        "retaliatory litigation"
    ],

    "control": [
        "silencing dissent",
        "suppression of faculty dissent",
        "risks attached to reporting abuse",
        "chilling effects",
        "self-censorship",
        "wrongful termination"
    ],

     "accountability_gaps": [
        "lack of accountability for powerful actors",
        "nepotism",
        "institutional protection",
        "conflict of interest",
        "power consolidation"
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
        "bullyism",
        "harassment",
        "DEI"
    ],

    "institutional_systems": [
        "ranking",
        "international universities",
        "higher education crisis"
    ],

    "geopolitics": [
        "politics",
        "authoritarianism",
        "democracy",
        "fascism",
        "war",
        "protest"
    ],

    "regions": [
        "united states",
        "europe",
        "asia",
        "africa",
        "australia",
        "latin america",
        "russia",
        "china",
        "ukraine",
        "iran",
        "lebanon",
        "israel",
        "palestine",
        "gaza"
    ],

    "temporal_psychological": [
        "future",
        "pessimism",
        "optimism"
    ]
}

def flatten_topics(topic_dict):
    return [
        item
        for sublist in topic_dict.values()
        for item in sublist
    ]

FLAT_MAAT_TOPICS = flatten_topics(MAAT_TOPICS)
topic_embeddings = model.encode(FLAT_MAAT_TOPICS, convert_to_tensor=True)



def build_matrix(articles, embeddings, topics, model):
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
                {"topic": topics[j], "score": float(scores[j])}
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


def clean_text(text):

    if not text:

        return ""

    soup = BeautifulSoup(text, "lxml")

    cleaned = soup.get_text(separator=" ")

    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()

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
    max_features=8,
    similarity_threshold=0.83
):

    candidate_topics = []

    # -----------------------------------
    # STEP 1: extract phrases per article
    # -----------------------------------

    for article in articles:

        text = build_semantic_text(article)

        if len(text.split()) < 30:
            continue

        try:

            vectorizer = TfidfVectorizer(
                stop_words="english",
                max_features=max_features,
                ngram_range=(1,3)
            )

            X = vectorizer.fit_transform([text])

            phrases = vectorizer.get_feature_names_out()

            for p in phrases:
                p = p.strip().lower()

                if len(p) < 4:
                    continue

                candidate_topics.append(p)

        except:
            continue

    # -----------------------------------
    # STEP 2: semantic deduplication
    # -----------------------------------

    unique_topics = []

    if not candidate_topics:
        return []

    embeddings = model.encode(
        candidate_topics,
        convert_to_tensor=True
    )

    for i, topic in enumerate(candidate_topics):

        keep = True

        for existing in unique_topics:

            sim = util.cos_sim(
                embeddings[i],
                existing["embedding"]
            ).item()

            if sim >= similarity_threshold:
                keep = False
                break

        if keep:
            unique_topics.append({
                "topic": topic,
                "embedding": embeddings[i]
            })

    # -----------------------------------
    # STEP 3: return clean topic list
    # -----------------------------------

    return [
        t["topic"]
        for t in unique_topics
    ]



# RUN

def run():

    path = sorted(Path("data/raw").glob("articles_*.jsonl"))[-1]
    date_str = path.stem.replace("articles_", "")

    articles = load_articles(path)
    embeddings = embed_articles(articles)

    discovered = extract_candidate_topics(articles)

    all_topics, overlap = resolve_topics(
        FLAT_MAAT_TOPICS,
        discovered,
        model
    )

    matrix = build_matrix(
        articles,
        embeddings,
        all_topics,
        model
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

