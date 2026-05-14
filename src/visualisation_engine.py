from pathlib import Path
import json

def latest_file(pattern):
    return sorted(Path("data/graphs").glob(pattern))[-1]

summary_path = latest_file("today_summary_*.json")

date_str = summary_path.stem.replace("today_summary_", "")

with open(summary_path, "r", encoding="utf-8") as f:
    summary = json.load(f)

lines = []

lines.append(f"# MAAT Daily Pulse")
lines.append("")
lines.append(f"## Top Themes Today ({date_str})")
lines.append("")
lines.append("| Topic | Articles | Avg Score |")
lines.append("|---|---:|---:|")

for item in summary:
    lines.append(
        f"| {item['topic']} | {item['count']} | {item['score']} |"
    )

Path("index.md").write_text(
    "\n".join(lines),
    encoding="utf-8"
)

