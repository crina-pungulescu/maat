import json
import math
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
from datetime import datetime


# ----------------------------
# CONFIG
# ----------------------------

THRESHOLD = 0.4
MIN_EDGE_COUNT = 3

def build_topic_hub_svg(npmi_edges, topic_cluster_map, nodes, date_str):
    import math

    output_dir = Path("docs/assets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # ----------------------------
    # 1. TAKE TOP EDGES (STRONGEST CONNECTIONS)
    # ----------------------------

    top_edges = sorted(
        npmi_edges,
        key=lambda x: x["npmi"],
        reverse=True
    )[:10]

    # ----------------------------
    # 2. COLLECT NODES IN GRAPH
    # ----------------------------

    node_ids = set()
    for e in top_edges:
        node_ids.add(e["source"])
        node_ids.add(e["target"])

    node_lookup = {n["id"]: n for n in nodes if n["id"] in node_ids}

    # ----------------------------
    # 3. SIMPLE FORCE-LIKE LAYOUT (CIRCULAR STABLE)
    # ----------------------------

    node_list = list(node_ids)
    n = len(node_list)

    radius = 220
    center_x, center_y = 300, 300

    positions = {}

    for i, node in enumerate(node_list):
        angle = (2 * math.pi * i) / max(n, 1)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        positions[node] = (x, y)

    # ----------------------------
    # 4. SVG BUILD
    # ----------------------------

    svg = []

    svg.append('<?xml version="1.0" encoding="UTF-8"?>')
    svg.append('<svg width="600" height="600" xmlns="http://www.w3.org/2000/svg">')

    # background
    svg.append('<rect width="100%" height="100%" fill="white"/>')

    # ----------------------------
    # EDGES
    # ----------------------------

    for e in top_edges:

        a, b = e["source"], e["target"]

        x1, y1 = positions[a]
        x2, y2 = positions[b]

        weight = e["npmi"]

        stroke_width = 1 + (weight * 3)

        svg.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="black" stroke-opacity="0.4" stroke-width="{stroke_width}"/>'
        )

    # ----------------------------
    # NODES
    # ----------------------------

    for node in node_list:

        x, y = positions[node]
        cluster = topic_cluster_map.get(node, "unknown")
        label = node_lookup.get(node, {}).get("label", node)

        svg.append(
            f'<circle cx="{x}" cy="{y}" r="6" fill="black"/>'
        )

        svg.append(
            f'<text x="{x+8}" y="{y+4}" font-size="10" '
            f'font-family="Arial">{label}</text>'
        )

        svg.append(
            f'<text x="{x+8}" y="{y+16}" font-size="8" fill="gray">'
            f'{cluster}</text>'
        )

    svg.append('</svg>')

    svg_content = "\n".join(svg)

    # ----------------------------
    # 5. WRITE FILES (DOUBLE EXPORT)
    # ----------------------------

    # stable file
    with open(output_dir / "topic_hub.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    # dated snapshot
    with open(output_dir / f"topic_hub_{date_str}.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)

    print("Topic hub SVG exported.")

def load_all_matrices():
    paths = sorted(Path("data/topics").glob("topic_matrix_*.json"))

    all_articles = []
    for p in paths:
        all_articles.extend(load_matrix(p))

    return all_articles

def run_aggregate():

    print("Processing AGGREGATE topic graph")

    matrix = load_all_matrices()

    date_str = "aggregate"

    topic_cluster_map = build_topic_cluster_map(matrix)

    nodes = build_nodes(matrix)
    edges = build_edges(matrix)

    pmi_edges, npmi_edges = build_pmi_edges(matrix, nodes)

    cross_pmi_edges = filter_cross_cluster_edges(pmi_edges, topic_cluster_map)
    cross_npmi_edges = filter_cross_cluster_edges(npmi_edges, topic_cluster_map)

    cluster_summary = build_cluster_summary(matrix, nodes, topic_cluster_map)

    cluster_edges = build_cluster_edges(cross_npmi_edges)

    summary = build_daily_summary(nodes)

    system = {
        "articles_total": len(matrix),
        "total_topics": len(nodes),
        "total_edges": len(edges),
        "cross_cluster_edges": len(cross_npmi_edges),
        "clusters": len(cluster_summary),
        "mode": "aggregate",
        "last_run": datetime.utcnow().isoformat()
    }

    write_system(system, date_str)

    save_outputs(
        nodes,
        edges,
        pmi_edges,
        npmi_edges,
        cross_pmi_edges,
        cross_npmi_edges,
        summary,
        cluster_summary,
        cluster_edges,
        date_str
    )

    print("AGGREGATE GRAPH COMPLETE")

def pretty_name(s: str) -> str:
    return s.replace("_", " ").replace("-", " ").title()

def write_system(system, date_str):
    path = f"data/graphs/system_{date_str}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(system, f, indent=2, ensure_ascii=False)

# ----------------------------
# LOAD
# ----------------------------

def load_matrix(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------
# CLUSTER MAPPING
# ----------------------------

def build_topic_cluster_map(matrix):

    mapping = {}

    for article in matrix:
        for t in article["scores"]:

            topic = t["topic"]
            cluster = t.get("cluster", "unknown")

            # stable assignment (first seen wins)
            if topic not in mapping:
                mapping[topic] = cluster

    return mapping


# ----------------------------
# NODES (TOPICS)
# ----------------------------

def build_nodes(matrix):

    topic_counts = Counter()
    topic_scores = defaultdict(list)

    for article in matrix:
        for t in article["scores"]:

            if t["score"] >= THRESHOLD:

                topic = t["topic"]

                topic_counts[topic] += 1
                topic_scores[topic].append(t["score"])

    nodes = []

    for topic, count in topic_counts.items():

        avg_score = sum(topic_scores[topic]) / len(topic_scores[topic])

        nodes.append({
            "id": topic,
            "label": pretty_name(topic),
            "weight": count,
            "avg_score": round(avg_score, 4)
        })

    return nodes


# ----------------------------
# EDGES (TOPIC CO-OCCURRENCE)
# ----------------------------

def build_edges(matrix):

    edge_counts = Counter()

    for article in matrix:

        topics = [
            t["topic"]
            for t in article["scores"]
            if t["score"] >= THRESHOLD
        ]

        unique_topics = sorted(set(topics))

        for a, b in combinations(unique_topics, 2):
            edge_counts[(a, b)] += 1

    edges = [
        {
            "source": a,
            "target": b,
            "weight": w
        }
        for (a, b), w in edge_counts.items()
    ]

    return sorted(edges, key=lambda x: x["weight"], reverse=True)


# ----------------------------
# PMI / NPMI EDGES
# ----------------------------

def build_pmi_edges(matrix, nodes):

    total_articles = len(matrix)

    node_counts = {n["id"]: n["weight"] for n in nodes}

    edge_counts = Counter()

    for article in matrix:

        topics = [
            t["topic"]
            for t in article["scores"]
            if t["score"] >= THRESHOLD
        ]

        unique_topics = sorted(set(topics))

        for a, b in combinations(unique_topics, 2):
            edge_counts[(a, b)] += 1

    pmi_edges = []
    npmi_edges = []

    for (a, b), co_count in edge_counts.items():

        if co_count < MIN_EDGE_COUNT:
            continue

        p_a = node_counts[a] / total_articles
        p_b = node_counts[b] / total_articles
        p_ab = co_count / total_articles

        pmi = math.log2((p_ab + 1e-12) / ((p_a * p_b) + 1e-12))
        npmi = pmi / (-math.log2(p_ab + 1e-12))

        pmi_edges.append({
            "source": a,
            "target": b,
            "co_occurrence": co_count,
            "pmi": round(pmi, 4)
        })

        npmi_edges.append({
            "source": a,
            "target": b,
            "co_occurrence": co_count,
            "npmi": round(npmi, 4)
        })

    return (
        sorted(pmi_edges, key=lambda x: x["pmi"], reverse=True),
        sorted(npmi_edges, key=lambda x: x["npmi"], reverse=True)
    )


# ----------------------------
# CROSS-CLUSTER FILTER
# ----------------------------

def filter_cross_cluster_edges(edges, topic_cluster_map):

    filtered = []

    for e in edges:

        a = e["source"]
        b = e["target"]

        ca = topic_cluster_map.get(a)
        cb = topic_cluster_map.get(b)

        if ca != cb:

            filtered.append({
                **e,
                "source_cluster": ca,
                "target_cluster": cb
            })

    return filtered


# ----------------------------
# CLUSTER SUMMARY (FOR INDEX TABLE)
# ----------------------------

def build_cluster_summary(matrix, nodes, topic_cluster_map):

    cluster_data = defaultdict(lambda: {
        "count": 0,
        "scores": [],
        "topics": set()
    })

    for node in nodes:

        topic = node["id"]
        cluster = topic_cluster_map.get(topic, "unknown")

        cluster_data[cluster]["count"] += node["weight"]
        cluster_data[cluster]["scores"].append(node["avg_score"])
        cluster_data[cluster]["topics"].add(topic)

    output = []

    for cluster, data in cluster_data.items():

        avg_score = (
            sum(data["scores"]) / len(data["scores"])
            if data["scores"] else 0
        )

        output.append({
            "topic": pretty_name(cluster),
            "count": data["count"],
            "score": round(avg_score, 4),
            "topics": sorted(list(data["topics"]))
        })

    return sorted(output, key=lambda x: x["count"], reverse=True)


# ----------------------------
# CLUSTER-LEVEL NETWORK
# ----------------------------

def build_cluster_edges(cross_edges):

    edge_counts = Counter()

    for e in cross_edges:

        a = e["source_cluster"]
        b = e["target_cluster"]

        if not a or not b:
            continue

        pair = tuple(sorted([a, b]))
        edge_counts[pair] += 1

    return [
        {
            "source": a,
            "target": b,
            "weight": w
        }
        for (a, b), w in edge_counts.items()
    ]


# ----------------------------
# DAILY SUMMARY (INDEX SIDEBAR)
# ----------------------------

def build_daily_summary(nodes, top_k=10):

    sorted_nodes = sorted(nodes, key=lambda x: x["weight"], reverse=True)

    return [
        {
            "topic": n["id"],
            "count": n["weight"],
            "score": n["avg_score"]
        }
        for n in sorted_nodes[:top_k]
    ]


# ----------------------------
# SAVE OUTPUTS
# ----------------------------

def save_outputs(
    nodes,
    edges,
    pmi_edges,
    npmi_edges,
    cross_pmi_edges,
    cross_npmi_edges,
    summary,
    cluster_summary,
    cluster_edges,
    date_str
):

    output_dir = Path("data/graphs")
    output_dir.mkdir(parents=True, exist_ok=True)

    def dump(name, data):
        with open(output_dir / name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    dump(f"graph_nodes_{date_str}.json", nodes)
    dump(f"graph_edges_{date_str}.json", edges)

    dump(f"pmi_edges_{date_str}.json", pmi_edges)
    dump(f"npmi_edges_{date_str}.json", npmi_edges)

    dump(f"cross_pmi_edges_{date_str}.json", cross_pmi_edges)
    dump(f"cross_npmi_edges_{date_str}.json", cross_npmi_edges)

    dump(f"today_summary_{date_str}.json", summary)

    dump(f"cluster_summary_{date_str}.json", cluster_summary)
    dump(f"cluster_edges_{date_str}.json", cluster_edges)

    print("Graph outputs saved.")


# ----------------------------
# PIPELINE
# ----------------------------

def run(mode):
    paths = sorted(Path("data/topics").glob("topic_matrix_*.json"))

    if mode == "daily":
        path = paths[-1]
        matrix = load_matrix(path)
        date_str = path.stem.replace("topic_matrix_", "")

    elif mode == "aggregate":
        matrix = load_all_matrices()
        date_str = "aggregate"

    else:
        raise ValueError("mode must be 'daily' or 'aggregate'")

    print(f"Processing {mode.upper()} topic graph")

    topic_cluster_map = build_topic_cluster_map(matrix)

    nodes = build_nodes(matrix)
    edges = build_edges(matrix)

    pmi_edges, npmi_edges = build_pmi_edges(matrix, nodes)

    cross_pmi_edges = filter_cross_cluster_edges(pmi_edges, topic_cluster_map)
    cross_npmi_edges = filter_cross_cluster_edges(npmi_edges, topic_cluster_map)

    cluster_summary = build_cluster_summary(matrix, nodes, topic_cluster_map)

    cluster_edges = build_cluster_edges(cross_npmi_edges)

    summary = build_daily_summary(nodes)

    system = {
        "mode": mode,
        "articles_total": len(matrix),
        "total_topics": len(nodes),
        "total_edges": len(edges),
        "cross_cluster_edges": len(cross_npmi_edges),
        "clusters": len(cluster_summary),
        "last_run": datetime.utcnow().isoformat()
    }

    write_system(system, date_str)

    save_outputs(
        nodes,
        edges,
        pmi_edges,
        npmi_edges,
        cross_pmi_edges,
        cross_npmi_edges,
        summary,
        cluster_summary,
        cluster_edges,
        date_str
    )

    build_topic_hub_svg(npmi_edges, topic_cluster_map, nodes, date_str)

    print(f"{mode.upper()} GRAPH COMPLETE")

if __name__ == "__main__":
    run("daily")
    run("aggregate")
