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

# ----------------------------

# CORE SEED TOPICS (your ontology anchor)

MAAT_TOPICS = [
    "governance",
    "reform",
    "policy",
    "funding",
    "student debt",
    "misconduct",
    "integrity",
    "ethics",
    "fraud",
    "abuse",
    "grade inflation",
    "academic standards",
    "plagiarism",
    "unpaid labour",
    "employment",
    "student experience",
    "faculty contracts",
    "academic careers",
    "adjuncts",
    "precarity",
    "ranking",
    "accreditation",
    "international universities",
    "higher education crisis",
    "title IX",
    "discrimination",
    "bullyism",
    "harrassement",
    "racisism",
    "exploitation",
    "power asymmetry",
    "nepotism",
    "retaliation",
    "litigation",
    "silencing dissent",
    "administrative coercion",
    "institutional opacity",
    "bureaucracy",
    "structural pressure enabling abuse",
    "scarcity systems producing exploitation",
    "hierarchy distorting fairness",
    "lack of accountability for powerful actors",
    "risks attached to reporting abuse",
    "authoritarianism",
    "palestine",
    "gaza",
    "israel",
    "politics",
    "fascism",
    "democracy",
    "future",
    "pessimism",
    "optimism",
    "united states",
    "europe",
    "asia",
    "war",
    "africa"
    "australia",
    "latin america",
    "russia",
    "china",
    "ukraine",
    "iran",
    "lebanon",
    "protest",
    "quality",
    "resources",
    "redundancy",
    "unemployment",
    "DEI"
]

topic_embeddings = model.encode(MAAT_TOPICS, convert_to_tensor=True)

# ----------------------------

# LOAD ARTICLES

# ----------------------------

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

# ----------------------------

# EMBEDDINGS FOR ARTICLES

# ----------------------------

def embed_articles(articles):

    texts = [

        build_semantic_text(a)

        for a in articles

    ]

    return model.encode(texts)


# ----------------------------

# EXISTING TOPIC MATCH

# ----------------------------

def assign_known_topics(article_emb):

    scores = util.cos_sim(article_emb, topic_embeddings)[0].cpu().numpy()

    return scores

# ----------------------------

# EMERGENT TOPIC DETECTION

# ----------------------------

def detect_emergent_topics(embeddings, articles, eps=0.22, min_samples=3):

    clustering = DBSCAN(
        eps=eps,
        min_samples=min_samples,
        metric="cosine"
    )

    labels = clustering.fit_predict(embeddings)

    clusters = {}

    for idx, label in enumerate(labels):

        if label == -1:
            continue

        clusters.setdefault(label, []).append(idx)

    discovered_topics = []

    for cluster_id, article_indices in clusters.items():

        texts = [

            build_semantic_text(articles[i])

            for i in article_indices

        ]

        try:

            vectorizer = TfidfVectorizer(
                max_features=10,
                stop_words="english",
                ngram_range=(1,2)
            )

            X = vectorizer.fit_transform(texts)

            keywords = vectorizer.get_feature_names_out()

            label = " | ".join(keywords[:4])

            discovered_topics.append({
                "label": label,
                "size": len(article_indices)
            })

        except:
            continue

    return discovered_topics
    
# ----------------------------


# MATRIX CONSTRUCTION

# ----------------------------

def build_topic_matrix(articles, embeddings, all_topics):

    topic_embeddings = model.encode(
        all_topics,
        convert_to_tensor=True
    )

    matrix = []

    for i, article in enumerate(articles):

        scores = util.cos_sim(
            embeddings[i],
            topic_embeddings
        )[0].cpu().numpy()

        topic_scores = []

        for idx, score in enumerate(scores):

            topic_scores.append({

                "topic": all_topics[idx],

                "score": round(float(score), 4)

            })

        topic_scores = sorted(
            topic_scores,
            key=lambda x: x["score"],
            reverse=True
        )

        matrix.append({

            "article_id": article.get("article_id"),

            "title": article.get("title"),

            "link": article.get("link"),

            "top_topics": topic_scores[:10],

            "all_scores": topic_scores

        })

    return matrix

# ----------------------------


# RUN

# ----------------------------

def run():

    path = sorted(
        Path("data/raw").glob("articles_*.jsonl")
    )[-1]

    date_str = path.stem.replace("articles_", "")

    articles = load_articles(path)

    embeddings = embed_articles(articles)

    # ---------------------------------
    # discover new semantic topics
    # ---------------------------------

    discovered = detect_emergent_topics(
        embeddings,
        articles
    )

    discovered_labels = [

        d["label"]

        for d in discovered

    ]

    # ---------------------------------
    # combine ontology + discovered
    # ---------------------------------

    all_topics = MAAT_TOPICS + discovered_labels

    # ---------------------------------
    # build semantic matrix
    # ---------------------------------

    matrix = build_topic_matrix(
        articles,
        embeddings,
        all_topics
    )

    # ---------------------------------
    # save outputs
    # ---------------------------------

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
        f"data/topics/discovered_topics_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(discovered, f, indent=2, ensure_ascii=False)

    print("MAAT semantic matrix complete")
