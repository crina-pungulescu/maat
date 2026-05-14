from pathlib import Path
import json

def latest_file(pattern):
    files = sorted(Path("data/graphs").glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files match {pattern}")
    return files[-1]

summary_path = latest_file("today_summary_*.json")

date_str = summary_path.stem.replace("today_summary_", "")

with open(summary_path, "r", encoding="utf-8") as f:
    summary = json.load(f)

total = sum(item["count"] for item in summary)

lines = []

lines.append("# MAAT Daily Pulse")
lines.append("")
lines.append(f"### Date: {date_str}")
lines.append("")
lines.append("## Top Signals")
lines.append("")
lines.append("| Rank | Topic | Articles | Share | Avg Score |")
lines.append("|---:|---|---:|---:|---:|")

for i, item in enumerate(summary, start=1):
    share = item["count"] / total if total else 0
    lines.append(
        f"| {i} | {item['topic']} | {item['count']} | {share:.1%} | {item['score']} |"
    )

top = summary[0] if summary else None

lines.append("")
lines.append("## Dominant Theme")
lines.append("")

if top:
    lines.append(f"**{top['topic']}** is leading today with {top['count']} mentions.")

lines.append("")
lines.append("## Signal Interpretation")
lines.append("")

if len(summary) >= 2:
    lines.append(
        f"Top 2 themes: {summary[0]['topic']} vs {summary[1]['topic']} → competing attention fields."
    )

Path("index.md").write_text("\n".join(lines), encoding="utf-8")
