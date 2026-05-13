import json

from pathlib import Path

from sentence_transformers import SentenceTransformer, util

import numpy as np

from sklearn.cluster import DBSCAN

from sklearn.feature_extraction.text import TfidfVectorizer

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# ----------------------------

# CORE SEED TOPICS (your ontology anchor)

MAAT_TOPICS = [
    "higher education governance",
    "university reform",
    "education policy",
    "funding of universities",
    "academic misconduct",
    "research integrity",
    "scientific fraud",
    "plagiarism in academia",
    "expected unpaid academic labour",
    "faculty employment",
    "student experience",
    "academic careers",
    "adjunct precarity",
    "ranking systems",
    "accreditation systems",
    "international universities",
    "higher education crisis",
    "title IX",
    "discrimination in academia",
    "bullyism in academia",
    "harrassement in academia",
    "racisism in academia",
    "exploitation in academia",
    "power asymmetry in academia",
    "unequal application of rules in academia",
    "retaliation in academia",
    "silencing dissent in academia",
    "administrative burden used coercively against faculty",
    "opacity in academia",
    "weaponised bureaucracy in academia",
    "insecure labour",
    "structural pressure enabling abuse",
    "scarcity systems producing exploitation",
    "elite hierarchy distorting fairness",
    "lack of accountability for powerful actors",
    "risks attached to reporting abuse"
]

topic_embeddings = model.encode(MAAT_TOPICS, convert_to_tensor=True)

# ----------------------------

# LOAD ARTICLES

# ----------------------------

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

        (a.get("title","") + " " + a.get("summary","") + " " + a.get("summary_en","") + " " + a.get("full_text","") + " " + a.get("translated_text",""))

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

def detect_emergent_topics(embeddings, articles, eps=0.25, min_samples=3):

    clustering = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")

    labels = clustering.fit_predict(embeddings)

    clusters = {}

    for label, article in zip(labels, articles):

        if label == -1:

            continue  # noise

        clusters.setdefault(label, []).append(article)

    emergent_topics = []

    for cluster_id, items in clusters.items():

        texts = [

            (a.get("title","") + " " + a.get("summary_en",""))

            for a in items

        ]

        # keyword extraction (cheap + effective)

        vectorizer = TfidfVectorizer(max_features=5, stop_words="english")

        X = vectorizer.fit_transform(texts)

        keywords = vectorizer.get_feature_names_out()

        label = " / ".join(keywords[:3])

        centroid = np.mean([

            embeddings[articles.index(a)] for a in items

        ], axis=0)

        emergent_topics.append({

            "label": label,

            "size": len(items),

            "articles": [

                {

                    "id": a.get("article_id"),

                    "title": a.get("title"),

                    "link": a.get("link")

                }

                for a in items

            ]

        })

    return emergent_topics

# ----------------------------

# MERGE WITH EXISTING ONTOLOGY

# ----------------------------

def merge_topics(articles, embeddings):

    salient_topics = {}

    unknown_articles = []

    for i, article in enumerate(articles):

        scores = assign_known_topics(embeddings[i])

        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score > 0.45:

            topic = MAAT_TOPICS[best_idx]

            salient_topics.setdefault(topic, {
                "count": 0,
                "articles": []
            })

            salient_topics[topic]["count"] += 1

            salient_topics[topic]["articles"].append({
                "id": article.get("article_id"),
                "title": article.get("title"),
                "link": article.get("link"),
                "score": round(best_score, 3)
            })

        else:
            unknown_articles.append(article)

    emergent = detect_emergent_topics(
        model.encode([
            a.get("title","") + " " + a.get("summary_en","")
            for a in unknown_articles
        ]),
        unknown_articles
    )

    return {
        "salient_topics": salient_topics,
        "emergent_topics": emergent,
        "total_articles": len(articles),
        "unclassified_articles": len(unknown_articles)
    }

# ----------------------------

# RUN

# ----------------------------

def run():

    path = sorted(Path("data/raw").glob("articles_*.jsonl"))[-1]

    articles = load_articles(path)

    embeddings = embed_articles(articles)

    result = merge_topics(articles, embeddings)

    Path("data/topics").mkdir(parents=True, exist_ok=True)

    with open("data/topics/topics_latest.json", "w", encoding="utf-8") as f:

        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Topic engine complete → emergent structure generated")

if __name__ == "__main__":

    run()
