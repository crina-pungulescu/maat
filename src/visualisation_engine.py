from pathlib import Path
from datetime import datetime
import json

def latest_file(pattern):

    files = sorted(Path("data/graphs").glob(pattern))

    if not files:

        raise FileNotFoundError(f"No files match {pattern}")

    return files[-1]

summary_path = latest_file("today_summary_*.json")

edges_path = latest_file("graph_edges_*.json")

nodes_path = latest_file("graph_nodes_*.json")

with open(summary_path, "r", encoding="utf-8") as f:

    summary = json.load(f)

with open(edges_path, "r", encoding="utf-8") as f:

    edges = json.load(f)

with open(nodes_path, "r", encoding="utf-8") as f:

    nodes = json.load(f)

DATA_DIR = Path("docs/_data")

DATA_DIR.mkdir(parents=True, exist_ok=True)

(DATA_DIR / "today_topics.json").write_text(

    json.dumps(summary, indent=2, ensure_ascii=False),

    encoding="utf-8"

)

(DATA_DIR / "topic_network.json").write_text(

    json.dumps(edges, indent=2, ensure_ascii=False),

    encoding="utf-8"

)

(DATA_DIR / "nodes.json").write_text(

    json.dumps(nodes, indent=2, ensure_ascii=False),

    encoding="utf-8"

)

system = {

    "articles_today": len(summary),

    "total_topics": len(nodes),

    "total_edges": len(edges),

    "last_run": datetime.utcnow().isoformat()

}

(DATA_DIR / "system.json").write_text(

    json.dumps(system, indent=2, ensure_ascii=False),

    encoding="utf-8"

)
