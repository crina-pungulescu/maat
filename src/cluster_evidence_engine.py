import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta


# ----------------------------
# LOAD HELPERS
# ----------------------------

def load_json(path):
    print(f"[LOAD] JSON -> {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path):
    print(f"[LOAD] JSONL -> {path}")
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    print(f"[LOAD] Loaded {len(rows)} rows from JSONL")
    return rows


def latest_file(pattern):
    files = sorted(Path("data/graphs").glob(pattern))
    if not files:
        raise FileNotFoundError(pattern)
    print(f"[LOAD] latest file -> {files[-1]}")
    return files[-1]

def files_last_n_days(paths, days=30):

    if not paths:
        return []

    latest_date = datetime.strptime(
        paths[-1].stem.split("_")[-1],
        "%Y-%m-%d"
    )

    cutoff = latest_date - timedelta(days=days - 1)

    filtered = []

    for path in paths:

        try:

            file_date = datetime.strptime(
                path.stem.split("_")[-1],
                "%Y-%m-%d"
            )

            if file_date >= cutoff:
                filtered.append(path)

        except Exception:
            continue

    print(
        f"[WINDOW] Using {len(filtered)} files "
        f"from {cutoff.date()} to {latest_date.date()}"
    )

    return filtered


# ----------------------------
# INPUTS
# ----------------------------

cluster_summary_path = latest_file("cluster_summary_aggregate_*.json")
graph_nodes_path = latest_file("graph_nodes_aggregate_*.json")

topic_matrix_paths = files_last_n_days(
    sorted(Path("data/topics").glob("topic_matrix_*.json")),
    days=30
)

raw_paths = files_last_n_days(
    sorted(Path("data/raw").glob("articles_*.jsonl")),
    days=30
)

cluster_summary = load_json(cluster_summary_path)
graph_nodes = load_json(graph_nodes_path)

print(f"[INPUT] clusters: {len(cluster_summary)}")
print(f"[INPUT] graph nodes: {len(graph_nodes)}")
print(f"[INPUT] topic_matrix files: {len(topic_matrix_paths)}")
print(f"[INPUT] raw article files: {len(raw_paths)}")


# ----------------------------
# INDEX: topic -> article_ids
# ----------------------------

topic_article_ids = {}

for node in graph_nodes:
    topic_article_ids[node["id"]] = set(node.get("article_ids", []))

print(f"[INDEX] topic_article_ids built: {len(topic_article_ids)} topics")


# ----------------------------
# INDEX: article -> topic scores
# ----------------------------

article_topic_scores = {}

print("[INDEX] building article_topic_scores...")

for path in topic_matrix_paths:
    matrix = load_json(path)

    for article in matrix:
        article_id = article["article_id"]

        if article_id not in article_topic_scores:
            article_topic_scores[article_id] = {}

        for t in article["scores"]:
            topic = t["topic"]
            score = t["score"]

            prev = article_topic_scores[article_id].get(topic, 0)
            if score > prev:
                article_topic_scores[article_id][topic] = score

print(f"[INDEX] article_topic_scores built: {len(article_topic_scores)} articles")


# ----------------------------
# INDEX: raw article metadata
# ----------------------------

raw_articles = {}

print("[INDEX] building raw article index...")

for path in raw_paths:
    rows = load_jsonl(path)

    for a in rows:
        raw_articles[a["article_id"]] = {
            "headline": a.get("headline") or a.get("title", ""),
            "url": a.get("url") or a.get("link", "")
        }

print(f"[INDEX] raw_articles built: {len(raw_articles)} articles")


# ----------------------------
# SELECT BEST EVIDENCE
# ----------------------------

used_articles = set()
cluster_evidence = []

print("[SELECT] starting cluster selection...\n")

for i, cluster in enumerate(cluster_summary):

    cluster_name = cluster["topic"]
    cluster_topics = cluster["topics"]

    print(f"[CLUSTER {i}] {cluster_name}")
    print(f"[CLUSTER {i}] topics: {len(cluster_topics)}")

    candidates = []

    for topic in cluster_topics:

        article_ids = topic_article_ids.get(topic, set())

        print(f"  [TOPIC] {topic} -> {len(article_ids)} articles")

        for article_id in article_ids:

            if article_id in used_articles:
                continue

            score = article_topic_scores.get(article_id, {}).get(topic, 0)

            candidates.append({
                "article_id": article_id,
                "topic": topic,
                "score": score
            })

    print(f"[CLUSTER {i}] candidates: {len(candidates)}")

    if not candidates:
        print(f"[CLUSTER {i}] SKIPPED (no candidates)\n")
        continue

    best = max(candidates, key=lambda x: x["score"])

    print(f"[CLUSTER {i}] BEST -> {best['article_id']} ({best['score']})\n")

    used_articles.add(best["article_id"])

    raw = raw_articles.get(best["article_id"], {})

    cluster_evidence.append({
        "cluster": cluster_name,
        "count": cluster["count"],
        "evidence": {
            "article_id": best["article_id"],
            "headline": raw.get("headline", ""),
            "url": raw.get("url", ""),
            "topic": best["topic"],
            "score": round(best["score"], 4)
        }
    })


# ----------------------------
# SAVE OUTPUT
# ----------------------------

latest_date = cluster_summary_path.stem.replace(
    "cluster_summary_aggregate_",
    ""
)

output_dir = Path("data/clusters")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / f"cluster_evidence_aggregate_{latest_date}.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cluster_evidence, f, indent=2, ensure_ascii=False)

print(f"[DONE] saved -> {output_path}")
print(f"[DONE] clusters written: {len(cluster_evidence)}")
