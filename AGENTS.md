# AGENTS.md

## Project identity

This repository is **ConsequenceEngine_v0**: a local-first historical consequence engine.

Its purpose is narrow:

> Given a bounded historical corpus and a root event, surface plausible first-, second-, and third-order effects with inspectable supporting evidence.

The first domain is **early COVID consequence cascades**:
panic buying, supply disruption, remote-work adoption, consumer behavior shifts, and downstream business effects.

The first corpus is a **local English Wikipedia multistream dump** plus a tiny human-curated seed set of pages.

This is a **historical scenario lab**. It is not a real-time forecaster, not a general chatbot, and not a full historical revision engine.

---

## First implementation principle

Build the smallest possible useful substrate first.

For prompt 1, the goal is **not** to build the consequence engine itself.
The goal is to build the local Wikipedia access layer that future prompts will use.

That means:

1. Read the local multistream index on Windows
2. Search page titles from the index
3. Resolve selected titles to offsets
4. Extract a very small number of matching pages from the compressed dump
5. Store extracted page content locally for reuse

If that works cleanly, later prompts can add normalization, graph construction, and canned consequence queries.

---

## Hard constraints

Keep code minimal.
Prefer a few clear files over many abstractions.
Prefer Python standard library unless a dependency clearly saves substantial complexity.
Assume Windows-first local development.
Do not require WSL.
Do not parse the entire dump.
Do not build a frontend.
Do not add embeddings, vector databases, or LLM orchestration in the first pass.

---

## First-pass non-goals

Do not build:

- a chat app
- a web UI
- a full graph engine
- an embeddings pipeline
- a large schema with speculative abstractions
- full-corpus parsing
- real-time forecasting behavior

---

## First milestone

The first milestone is a CLI flow like this:

1. Search titles for a query such as "COVID", "Zoom Video Communications", or "Panic buying"
2. Show matching titles and index metadata
3. Select a few exact pages
4. Extract those pages from the dump
5. Save them into a small local SQLite database or local cache
6. Print a short confirmation summary

A successful first milestone is boring but solid.

---

## Preferred repo shape

ConsequenceEngine_v0/
  src/
    ce/
      __init__.py
      config.py
      wiki.py
      store.py
  scripts/
    search_titles.py
    extract_pages.py
  local_data/        # gitignored
  output/            # gitignored
  tests/
  README.md
  AGENTS.md

Keep `wiki.py` responsible for index reading, title search, and page extraction.
Keep `store.py` responsible for the tiny local SQLite cache.

Avoid creating extra modules until there is pressure for them.

---

## Data assumptions

The Wikipedia dump and index live under `local_data/` and are not committed to git.

Use config variables for local paths.
Do not hardcode absolute machine-specific paths into logic.

Prefer reading the `.xml.bz2` directly if feasible.
If direct multistream extraction becomes too awkward, it is acceptable to make a narrow local workaround, but do not explode scope.

---

## Codex behavior expectations

When modifying this repo:

- optimize for the narrowest working vertical slice
- avoid speculative abstractions
- keep functions small and inspectable
- add only the minimum code needed for the milestone
- explain assumptions briefly
- prefer local CLI verification steps
- preserve Windows compatibility

If a tradeoff appears between "clean architecture" and "fewest moving parts that work", prefer the latter for v0.