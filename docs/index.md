---
theme: jekyll-theme-cayman
---

# MA'AT 
# Multilingual Archive for Academic Transparency
*A computational observatory of global higher education discourse*

---

## Abstract

MAAT is a multilingual information system that observes how higher education is discussed across global media, policy documents, and institutional sources. It aggregates RSS feeds from diverse linguistic ecosystems and transforms them into a structured dataset using semantic filtering and language-agnostic embeddings.

The system does not aim to summarize events, but to map recurring patterns in how universities, governance structures, and academic systems are described across the world.

---

## Problem

Higher education discourse is fragmented across languages, institutions, and media systems. Policy debates in Europe, journalistic coverage in the United States, and institutional communications in Asia rarely share a unified semantic frame.

As a result, global patterns in academic governance, funding, labour, and reform remain difficult to observe at scale.

MAAT explores whether these fragmented narratives can be aligned through a minimal semantic layer.

---

## System Overview

MAAT operates as a continuous ingestion pipeline:

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

MAAT depends on RSS availability and successful article extraction. Paywalled content, incomplete feeds, and extraction failures reduce coverage. Semantic filtering also introduces bias toward conceptually explicit texts, potentially underrepresenting implicit or emergent discourse.

---

## Future Directions

- longitudinal mapping of policy narratives  
- cross-country discourse comparison  
- institutional actor tracking  
- temporal evolution of semantic clusters  
- visualisation of global higher education “attention fields”
