---
theme: jekyll-theme-cayman
---

<h1 style="font-size: 3.2em; margin-bottom: 0.2em; text-align: center; line-height: 1.1;">

MA'AT:<br>

<span style="font-weight: 400; font-size: 0.90em;">

<b>M</b>ultilingual <b>A</b>rchive for <b>A</b>cademic <b>T</b>ransparency

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

<ul>
<li>Articles ingested today: {{ site.data.system.articles_today }}</li>
<li>Total stored articles: {{ site.data.system.total_articles }}</li>
<li>Feeds active: {{ site.data.system.feeds_active }}</li>
<li>Last run: {{ site.data.system.last_run }}</li>
</ul>

---

## Dominant Themes Today

<table>
<tr>
<th>Topic</th>
<th>Articles</th>
<th>Mean Score</th>
</tr>

{% for topic in site.data.today_topics %}
<tr>
<td>{{ topic.topic }}</td>
<td>{{ topic.count }}</td>
<td>{{ topic.score }}</td>
</tr>
{% endfor %}

</table>

---

## Strongest Topic Connections

<ul>
{% for edge in site.data.topic_network %}
<li>
{{ edge.source }} ↔ {{ edge.target }}
({{ edge.weight }})
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

