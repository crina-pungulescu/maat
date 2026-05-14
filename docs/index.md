---
theme: jekyll-theme-cayman
---

<h1 style="font-size: 3.2em; margin-bottom: 0.2em; text-align: center; line-height: 1.1;">

MA'AT:<br>

<span style="font-weight: 400; font-size: 0.90em;">

<b>M</b>ultilingual <b>A</b>rchive for <b>A</b>cademic <b>T</b>opology

</span>

</h1>

# *A computational observatory of global higher education discourse*

---

## Abstract

MA'AT is a multilingual information system that observes how higher education is discussed across global media, policy documents, and institutional sources. It aggregates RSS feeds from diverse linguistic ecosystems and transforms them into a structured dataset using semantic filtering and language-agnostic embeddings.

The system aims to map recurring patterns in how universities, governance structures, and academic systems are evolving across the world.

---

## System Overview

MA'AT operates as a continuous ingestion pipeline:

- RSS feeds from global academic, policy, and journalistic sources  
- multilingual embedding model for semantic comparison  
- relevance filtering against a curated conceptual space  
- language detection and optional translation  
- deduplication and structured storage  

Each article is evaluated not by keywords, but by semantic proximity to higher education-related concepts.

---

## System Status
{% assign system = site.data.system %}

<ul>
<li>Articles ingested today: {{ system.articles_today | default: "—" }}</li>
<li>Total stored articles: {{ system.total_articles | default: "—" }}</li>
<li>Feeds active: {{ system.feeds_active | default: "—" }}</li>
<li>Last run: {{ system.last_run | default: "—" }}</li>
</ul>

---

## Dominant Themes Today

{% assign topics = site.data.today_topics %}

<table>
<tr>
<th>Topic</th>
<th>Articles</th>
<th>Mean Semantic Similarity Score</th>
</tr>

{% for topic in topics %}
<tr>
<td>{{ topic.topic }}</td>
<td>{{ topic.count }}</td>
<td>{{ topic.score }}</td>
</tr>
{% endfor %}

</table>

---

## Top Signals

| Rank | Topic | Articles | Share | Avg Score |
|---:|---|---:|---:|---:|
| 1 | student engagement | 46 | 15.9% | 0.4417 |
| 2 | academic abuse | 34 | 11.7% | 0.4519 |
| 3 | academic exploitation | 30 | 10.3% | 0.4603 |
| 4 | academic freedom | 28 | 9.7% | 0.4523 |
| 5 | suppression of faculty dissent | 28 | 9.7% | 0.4633 |
| 6 | higher education crisis | 27 | 9.3% | 0.4884 |
| 7 | pedagogy | 25 | 8.6% | 0.4802 |
| 8 | university administration | 25 | 8.6% | 0.4626 |
| 9 | institutional opacity | 24 | 8.3% | 0.4781 |
| 10 | future of higher education | 23 | 7.9% | 0.4511 |

---

## Strongest Topic Connections

{% assign network = site.data.topic_network %}

<ul>
{% for edge in network %}
<li>
{{ edge.source }} ↔ {{ edge.target }} ({{ edge.weight }})
</li>
{% endfor %}
</ul>

---

## Limitations

MA'AT depends on RSS availability and successful article extraction. Paywalled content, incomplete feeds, and extraction failures reduce coverage. Semantic filtering also introduces bias toward conceptually explicit texts, potentially underrepresenting implicit or emergent discourse.

---

## Future Directions

- longitudinal mapping of policy narratives  
- cross-country discourse comparison  
- institutional actor tracking  
- temporal evolution of semantic clusters  
- visualisation of global higher education “attention fields”

