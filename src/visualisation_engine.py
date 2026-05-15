from pathlib import Path
from datetime import datetime
import json


# ----------------------------
# UTIL
# ----------------------------

from pathlib import Path

def count_total_articles():

    total = 0

    for file in Path("data/raw").glob("articles_*.jsonl"):

        with open(file, "r", encoding="utf-8") as f:
            total += sum(1 for _ in f)

    return total

def latest_file(pattern):
    files = sorted(Path("data/graphs").glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files match {pattern}")
    return files[-1]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------
# LOAD GRAPH OUTPUTS
# ----------------------------

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
