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

The system does not aim to summarize events, but to map recurring patterns in how universities, governance structures, and academic systems are described across the world.

---

## Problem

Higher education discourse is fragmented across languages, institutions, and media systems. Policy debates in Europe, journalistic coverage in the United States, and institutional communications in Asia rarely share a unified semantic frame.

As a result, global patterns in academic governance, funding, labour, and reform remain difficult to observe at scale.

MA'AT explores whether these fragmented narratives can be aligned through a minimal semantic layer.

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

## Output

The system produces daily JSONL datasets containing:

- article metadata (title, source, journal, link)
- full extracted text
- detected language
- normalised English summary
- semantic relevance score
- unique article identifier
- ingestion timestamp

This structure enables downstream analysis of discourse evolution, clustering, and comparative policy mapping.

---

## Design Principles

- **Semantic filtering over keyword matching**
- **Multilingual parity as default**
- **Signal extraction over content accumulation**
- **Traceable data provenance**
- **Minimal human labeling**

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


## Page Analytics

<div style="display:flex; gap:20px; justify-content:center; margin:20px 0;">

<div style="padding:10px; border:1px solid #ddd; border-radius:8px;">

<b>🌍 Visitors (7d)</b><br>

{{ site.data.analytics.visitors_week }}

</div>

<div style="padding:10px; border:1px solid #ddd; border-radius:8px;">

<b>📈 Today</b><br>

{{ site.data.analytics.visitors_today }}

</div>

<div style="padding:10px; border:1px solid #ddd; border-radius:8px;">

<b>🧭 Avg Time</b><br>

{{ site.data.analytics.avg_time }}

</div>

</div>

## System Status

<h2>System Status</h2>

<ul>

<li>📥 Articles ingested today: {{ site.data.system.articles_today }}</li>

<li>📦 Total stored articles: {{ site.data.system.total_articles }}</li>

<li>🌐 Feeds active: {{ site.data.system.feeds_active }}</li>

<li>⚡ Last run: {{ site.data.system.last_run }}</li>

</ul>

## Today's Signals

<h2>Today’s Signals</h2>

<ul>
{% for article in site.data.articles_today %}
<li>
<a href="{{ article.link }}">{{ article.title }}</a>
<br>
<small>{{ article.journal }} · {{ article.language }}</small>
</li>
{% endfor %}
</ul>

## Emergent Topics

<h2>Emergent Topics (last 24h)</h2>

<div style="display:flex; flex-wrap:wrap; gap:8px;">

<span style="padding:6px 10px; border-radius:999px; border:1px solid #ccc;">
academic funding (12)
</span>

<span style="padding:6px 10px; border-radius:999px; border:1px solid #ccc;">
university governance (9)
</span>

<span style="padding:6px 10px; border-radius:999px; border:1px solid #ccc;">
research misconduct (6)
</span>

</div>
