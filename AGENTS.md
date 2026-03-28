# AGENTS.md

## Project identity

This repository is the beginning of **CE_v0**: a local-first historical consequence engine.

The purpose of CE_v0 is **not** to be a general chatbot, a live news scraper, a RAG playground, or a real-time geopolitical oracle.

The purpose of CE_v0 is to explore a narrower and more disciplined question:

> Given a bounded corpus and a root event, what are the most plausible first-, second-, and third-order effects, and what observable triggers or indicators support those branches?

The first domain is **early COVID consequence cascades**, especially panic buying, supply disruption, consumer behavior shifts, remote-work adoption, and downstream business effects.

The first source corpus is a **local English Wikipedia dump** plus a small human-curated seed set of relevant pages.

This is a **historical scenario lab**, not a true “as-of” forecasting system. The current Wikipedia dump is retrospective current-content data, not a full revision-history corpus.

---

## v0 goals

The first version should prove out these ideas:

1. Read a local Wikipedia multistream index on Windows
2. Search page titles from the local dump index
3. Extract a very small number of selected pages from the compressed dump
4. Normalize those pages into structured local records
5. Store the normalized records in SQLite
6. Build a small human-inspectable consequence graph from a curated subset of pages
7. Run a canned historical question over that graph
8. Return likely first-, second-, and third-order effects with simple confidence/probability-like scores and supporting evidence pointers

A successful v0 is not “smart.” A successful v0 is **inspectable, grounded, local, and narrow**.

---

## Explicit non-goals

Do **not** turn this into any of the following:

- a generic chat app
- a live news ingestion platform
- an Ollama playground
- an embeddings-first architecture
- a vector database demo
- a giant frontend-heavy app before the data model is stable
- a true real-time forecasting engine
- a true historical “as-of date” forecaster
- an attempt to parse the entire Wikipedia dump on day one

Do **not** optimize for breadth. Optimize for a narrow, working vertical slice.

---

## First scenario family

The initial scenario family is:

- early COVID disruptions
- panic buying and consumer hoarding
- supply chain strain
- remote work acceleration
- business winners/losers
- downstream behavior effects

Example questions include:

- What were the likely first-, second-, and third-order effects of early COVID panic buying?
- What downstream effects followed the expectation of lockdowns and supply disruption?
- Which business categories were likely to benefit from stay-at-home behavior?
- Which observable signals would support a branch where remote-work tools surge?

The system may eventually talk about assets or companies such as Zoom or Netflix, but v0 should focus primarily on **consequence chains**, not financial advice.

---

## Corpus and data principles

The Wikipedia dump is a **local optional corpus dependency**, not tracked repo content.

Large raw data files must **not** be committed to git.

Use gitignored local folders such as:

- `local_data/`
- `output/`

The compressed Wikipedia XML dump should remain compressed if possible.

Prefer reading the `.xml.bz2` directly from Python rather than fully decompressing it immediately.

The decompressed multistream index may exist locally for faster development, but it must remain outside source control.

Start from a **tiny subset of pages**. Do not attempt full-corpus parsing in the first pass.

---

## Architectural principles

### 1. Graph-first, not embedding-first

The central object is a **consequence graph**, not a vector index and not a chat history.

The system should reason over:

- normalized pages
- entities
- events
- claims
- consequence nodes
- edges between consequence nodes
- supporting evidence links

Embeddings may be added later if they clearly help retrieval, but they are not the core engine in v0.

### 2. Human-assisted first pass

The first graph-building flow should be human-assisted.

The system may propose candidate nodes or edges, but the graph must remain inspectable and editable.

Do not pretend the first version can infer a trustworthy world model automatically.

### 3. CLI-first

The first usable interface should be CLI-first.

Reason:
- easier debugging
- easier parser iteration
- less UI churn
- better fit for a blank repo and unstable schemas

A small local web UI may be added later only after the core objects stabilize.

### 4. Windows-friendly

Assume a Windows-first local development environment.

Do not require WSL unless there is a strong technical reason.

Prefer Python standard library or lightweight dependencies where possible.

### 5. SQLite-first

Use SQLite for normalized records and graph data in v0.

Avoid premature infrastructure.

---

## Proposed repo shape

```text
CE_v0/
  src/
    ce/
      __init__.py
      config.py
      db.py
      wiki_index.py
      wiki_extract.py
      normalize.py
      graph_build.py
      scenarios.py
      models.py
  scripts/
    inspect_index.py
    extract_pages.py
    build_seed_graph.py
    run_canned_question.py
  tests/
  data/
    fixtures/
  local_data/         # gitignored
  output/             # gitignored
  README.md
  AGENTS.md
  .env.example