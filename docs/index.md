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

## Design Principles

- **Semantic filtering over keyword matching**
- **Multilingual parity as default**
- **Signal extraction over content accumulation**
- **Traceable data provenance**
- **Minimal human labeling**

<h2 style="margin-top: 2em;">Salient Themes</h2>

<p style="opacity:0.7; margin-top:-0.5em;">
Most prominent thematic concentrations across the current corpus.
</p>

<div style="
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
    margin-top: 1em;
">

{% for theme in site.data.salient_themes %}
  <div style="
      border: 1px solid #ddd;
      border-radius: 10px;
      padding: 12px;
      background: #fafafa;
  ">
    
    <div style="font-weight: 600; font-size: 1.05em;">
      {{ theme.theme }}
    </div>

    <div style="margin-top: 6px; font-size: 0.9em; opacity: 0.75;">
      Mentions: {{ theme.count }}
    </div>

    <div style="margin-top: 6px; font-size: 0.85em; opacity: 0.6;">
      Salience: {{ theme.score }}
    </div>

    <div style="
        margin-top: 8px;
        height: 6px;
        background: #eee;
        border-radius: 999px;
        overflow: hidden;
    ">
      <div style="
          width: {{ theme.score | times: 100 }}%;
          height: 100%;
          background: #4a6cf7;
      "></div>
    </div>

  </div>
{% endfor %}

</div>

<h2>Emergent Topics</h2>

<p style="opacity:0.7; margin-top:-0.5em;">
Automatically detected nascent thematic structures that are surfacing across the corpus, indicating early formation of new discourse patterns.
</p>

<div style="display:flex; flex-wrap:wrap; gap:8px;">

<span style="padding:6px 10px; border-radius:999px; border:1px solid #ccc;">

</span>

<span style="padding:6px 10px; border-radius:999px; border:1px solid #ccc;">

</span>

<span style="padding:6px 10px; border-radius:999px; border:1px solid #ccc;">

</span>

</div>

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

<h2>System Status</h2>

<ul>

<li> Articles ingested today: {{ site.data.system.articles_today }}</li>

<li> Total stored articles: {{ site.data.system.total_articles }}</li>

<li> Feeds active: {{ site.data.system.feeds_active }}</li>

<li> Last run: {{ site.data.system.last_run }}</li>

</ul>

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

