import json
import math

from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations


THRESHOLD = 0.4
MIN_EDGE_COUNT = 3


# ----------------------------
# LOAD
# ----------------------------

def load_matrix(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------
# NODE BUILDING
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

        avg_score = (
            sum(topic_scores[topic]) /
            len(topic_scores[topic])
        )

        nodes.append({
            "id": topic,
            "weight": count,
            "avg_score": round(avg_score, 4)
        })

    return nodes


# ----------------------------
# EDGE BUILDING
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

    edges.sort(
        key=lambda x: x["weight"],
        reverse=True
    )

    return edges


# ----------------------------
# PMI + NPMI EDGE BUILDING
# ----------------------------

def build_pmi_edges(matrix, nodes):

    total_articles = len(matrix)

    # topic frequencies
    node_counts = {
        n["id"]: n["weight"]
        for n in nodes
    }

    # co-occurrence frequencies
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

        # ignore weak accidental pairings
        if co_count < MIN_EDGE_COUNT:
            continue

        p_a = node_counts[a] / total_articles
        p_b = node_counts[b] / total_articles
        p_ab = co_count / total_articles

        # PMI
        pmi = math.log2(
            (p_ab + 1e-12) /
            ((p_a * p_b) + 1e-12)
        )

        # NPMI
        npmi = pmi / (
            -math.log2(p_ab + 1e-12)
        )

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

    # strongest relationships first
    pmi_edges.sort(
        key=lambda x: x["pmi"],
        reverse=True
    )

    npmi_edges.sort(
        key=lambda x: x["npmi"],
        reverse=True
    )

    return pmi_edges, npmi_edges


# ----------------------------
# DAILY SUMMARY
# ----------------------------

def build_daily_summary(nodes, top_k=10):

    sorted_nodes = sorted(
        nodes,
        key=lambda x: x["weight"],
        reverse=True
    )

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
    summary,
    date_str
):

    output_dir = Path("data/graphs")
    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        f"data/graphs/graph_nodes_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            nodes,
            f,
            indent=2,
            ensure_ascii=False
        )

    with open(
        f"data/graphs/graph_edges_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            edges,
            f,
            indent=2,
            ensure_ascii=False
        )

    with open(
        f"data/graphs/pmi_edges_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            pmi_edges,
            f,
            indent=2,
            ensure_ascii=False
        )

    with open(
        f"data/graphs/npmi_edges_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            npmi_edges,
            f,
            indent=2,
            ensure_ascii=False
        )

    with open(
        f"data/graphs/today_summary_{date_str}.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            summary,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("Graph outputs saved.")


# ----------------------------
# RUN PIPELINE
# ----------------------------

def run():

    path = sorted(
        Path("data/topics").glob(
            "topic_matrix_*.json"
        )
    )[-1]

    date_str = path.stem.replace(
        "topic_matrix_",
        ""
    )

    print(
        f"Processing topic graph for: {date_str}"
    )

    matrix = load_matrix(path)

    nodes = build_nodes(matrix)

    edges = build_edges(matrix)

    pmi_edges, npmi_edges = build_pmi_edges(
        matrix,
        nodes
    )

    summary = build_daily_summary(nodes)

    print("CWD:", Path.cwd())

    print(
        "OUTPUT EXPECTED:",
        Path("data/graphs").resolve()
    )

    save_outputs(
        nodes,
        edges,
        pmi_edges,
        npmi_edges,
        summary,
        date_str
    )

    print("MAAT TOPIC GRAPH COMPLETE")


# ----------------------------
# ENTRY POINT
# ----------------------------

if __name__ == "__main__":

    run()
