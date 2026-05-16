from pathlib import Path
from datetime import datetime
import json


# ----------------------------
# UTIL
# ----------------------------

def count_total_articles():
    total = 0

    for file in Path("data/raw").glob("articles_*.jsonl"):
        with open(file, "r", encoding="utf-8") as f:
            total += sum(1 for _ in f)

    return total


def latest_file(directory, pattern):
    files = sorted(Path(directory).glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files match {pattern}")
    return files[-1]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------
# LOAD INPUTS
# ----------------------------

cluster_summary_path = latest_file("data/graphs", "cluster_summary_*.json")
evidence_path = latest_file("data/clusters", "cluster_evidence_*.json")
network_path = latest_file("data/graphs", "cross_npmi_edges_*.json")
system_path = latest_file("data/graphs", "system_*.json")

cluster_summary = load_json(cluster_summary_path)
cluster_evidence = load_json(evidence_path)
cross_npmi_network = load_json(network_path)
system = load_json(system_path)

system["total_articles"] = count_total_articles()


print(f"[LOAD] clusters: {len(cluster_summary)}")
print(f"[LOAD] evidence: {len(cluster_evidence)}")


# ----------------------------
# INDEX EVIDENCE BY CLUSTER
# ----------------------------

evidence_map = {}

for item in cluster_evidence:
    evidence_map[item["cluster"]] = item["evidence"]


# ----------------------------
# MERGE CLUSTER + EVIDENCE
# ----------------------------

enriched_clusters = []

for cluster in cluster_summary:

    name = cluster["topic"]

    enriched_clusters.append({
        "topic": name,
        "count": cluster["count"],
        "score": cluster.get("score", 0),
        "topics": cluster["topics"],
        "evidence": evidence_map.get(name, {
            "headline": "",
            "url": "",
            "article_id": "",
            "score": 0
        })
    })


print(f"[MERGE] enriched clusters: {len(enriched_clusters)}")


# ----------------------------
# WRITE JEKYLL DATA
# ----------------------------

DATA_DIR = Path("docs/_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


(DATA_DIR / "cluster_summary.json").write_text(
    json.dumps(enriched_clusters, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

(DATA_DIR / "cross_npmi_network.json").write_text(
    json.dumps(cross_npmi_network, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

(DATA_DIR / "system.json").write_text(
    json.dumps(system, indent=2, ensure_ascii=False),
    encoding="utf-8"
)


print("[DONE] Visualisation layer updated.")# ----------------------------

cluster_path = latest_file("cluster_summary_*.json")
network_path = latest_file("cross_npmi_edges_*.json")
system_path = latest_file("system_*.json")


cluster_summary = load_json(cluster_path)
cross_npmi_network = load_json(network_path)
system = load_json(system_path)

system["total_articles"] = count_total_articles()


# ----------------------------
# WRITE JEKYLL DATA
# ----------------------------

DATA_DIR = Path("docs/_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


# Dominant Themes (clusters)
(DATA_DIR / "cluster_summary.json").write_text(
    json.dumps(cluster_summary, indent=2, ensure_ascii=False),
    encoding="utf-8"
)


# Cross-cluster strongest links
(DATA_DIR / "cross_npmi_network.json").write_text(
    json.dumps(cross_npmi_network, indent=2, ensure_ascii=False),
    encoding="utf-8"
)


# System status (pure metadata)
(DATA_DIR / "system.json").write_text(
    json.dumps(system, indent=2, ensure_ascii=False),
    encoding="utf-8"
)


print("Visualisation layer updated.")
