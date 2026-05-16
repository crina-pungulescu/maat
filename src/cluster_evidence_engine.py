import json
from pathlib import Path


# ----------------------------
# LOAD HELPERS
# ----------------------------

def latest_file(directory, pattern):

    files = sorted(Path(directory).glob(pattern))

    if not files:
        raise FileNotFoundError(f"No files match {pattern}")

    return files[-1]


def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):

    rows = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    return rows


# ----------------------------
# LOAD INPUTS
# ----------------------------

cluster_summary_path = latest_file(
    "data/graphs",
    "cluster_summary_aggregate_*.json"
)

graph_nodes_path = latest_file(
    "data/graphs",
    "graph_nodes_aggregate_*.json"
)

topic_matrix_paths = sorted(
    Path("data/topics").glob("topic_matrix_*.json")
)

raw_paths = sorted(
    Path("data/raw").glob("articles_*.jsonl")
)


cluster_summary = load_json(cluster_summary_path)
graph_nodes = load_json(graph_nodes_path)


# ----------------------------
# BUILD TOPIC -> ARTICLE IDS
# ----------------------------

topic_article_ids = {}

for node in graph_nodes:

    topic_article_ids[node["id"]] = set(
        node.get("article_ids", [])
    )


# ----------------------------
# BUILD ARTICLE SCORE INDEX
# ----------------------------

article_topic_scores = {}

for path in topic_matrix_paths:

    matrix = load_json(path)

    for article in matrix:

        article_id = article["article_id"]

        if article_id not in article_topic_scores:
            article_topic_scores[article_id] = {}

        for t in article["scores"]:

            topic = t["topic"]
            score = t["score"]

            existing = article_topic_scores[article_id].get(topic, 0)

            if score > existing:
                article_topic_scores[article_id][topic] = score


# ----------------------------
# BUILD RAW ARTICLE INDEX
# ----------------------------

raw_articles = {}

for path in raw_paths:

    rows = load_jsonl(path)

    for article in rows:

        article_id = article["article_id"]

        raw_articles[article_id] = {
            "headline": (
                article.get("headline")
                or article.get("title")
                or ""
            ),
            "url": (
                article.get("url")
                or article.get("link")
                or ""
            )
        }


# ----------------------------
# SELECT BEST EVIDENCE
# ----------------------------

used_articles = set()

cluster_evidence = []

for cluster in cluster_summary:

    cluster_name = cluster["topic"]
    cluster_count = cluster["count"]

    cluster_topics = set(cluster["topics"])

    candidates = []

    for topic in cluster_topics:

        article_ids = topic_article_ids.get(topic, set())

        for article_id in article_ids:

            if article_id in used_articles:
                continue

            score = article_topic_scores.get(
                article_id,
                {}
            ).get(topic, 0)

            candidates.append({
                "article_id": article_id,
                "topic": topic,
                "score": score
            })

    if not candidates:
        continue

    best = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    )[0]

    used_articles.add(best["article_id"])

    raw = raw_articles.get(best["article_id"], {})

    cluster_evidence.append({
        "cluster": cluster_name,
        "count": cluster_count,
        "evidence": {
            "article_id": best["article_id"],
            "headline": raw.get("headline", ""),
            "url": raw.get("url", ""),
            "topic": best["topic"],
            "score": round(best["score"], 4)
        }
    })


# ----------------------------
# SAVE
# ----------------------------

latest_date = (
    cluster_summary_path.stem
    .replace("cluster_summary_aggregate_", "")
)

output_dir = Path("data/clusters")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = (
    output_dir
    / f"cluster_evidence_aggregate_{latest_date}.json"
)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(
        cluster_evidence,
        f,
        indent=2,
        ensure_ascii=False
    )

print("Cluster evidence exported.")
