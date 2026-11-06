---
name: pros-graph
description: Inspects codebase relationships with Graphify. Use for large repository exploration, tracing how modules connect, or /pros-graph.
argument-hint: "<question | path A B | explain X | update>"
---

# Inspect the code graph

Request: $ARGUMENTS

Use this when a graph will answer faster than searching. For a small repo or a known file, read the file instead.

1. If `graphify` is missing, say so and use normal search.
2. If `graphify-out/graph.json` is missing, ask before building it. Build with `graphify update .`. This is local, with no LLM calls.
3. If the graph is stale, run `graphify update .`. Don't rebuild it when nothing changed.
4. Answer from the graph, then read only the files it points to:
   - `graphify query "<question>" --budget 1000` (ask narrow questions; broad ones can exceed the budget)
   - `graphify path "A" "B"`
   - `graphify explain "X"`

Don't run `graphify install`, `graphify hook install`, `graphify watch` or `graphify extract` unless the user asks. `extract` calls an LLM, and the others add hooks or background work.

Graphs don't always save tokens. Run `graphify benchmark` or `pros tokens` to measure a real repo.

Check that `graphify-out/` is ignored by git. If it isn't, tell the user.
