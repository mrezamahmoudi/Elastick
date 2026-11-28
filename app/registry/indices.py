"""Registry entries: index-management APIs (raw ES paths)."""

from .core import E

ENTRIES = [
    E("PUT", "/{index}", "Indices", "Create index",
      "Creates an index with optional settings, mappings and aliases supplied "
      "in the body. By default fails if the index exists; pass "
      "`op_type=create` to get the same behavior explicitly."),
    E("DELETE", "/{index}", "Indices", "Delete index",
      "**Destructive — irreversible.** Deletes the index and all of its "
      "documents, settings, mappings and shards."),
    E("HEAD", "/{index}", "Indices", "Check index exists",
      "Lightweight existence check: HTTP 200 if the index exists, 404 if not."),
    E("GET", "/{index}", "Indices", "Get index info",
      "Full definition of the index: aliases, mappings, settings. The "
      "one-stop view of *what this index is*."),
    E("POST", "/{index}/_open", "Indices", "Open index",
      "Reopens a previously closed index, making it searchable again and "
      "recovering its shards."),
    E("POST", "/{index}/_close", "Indices", "Close index",
      "Closes an index: shards are removed from nodes and search/write fail. "
      "Cheap way to freeze old data without deleting it."),
    E("GET", "/{index}/_mapping", "Indices", "Get mapping",
      "Field definitions for the index: every field, its type and indexing "
      "options. Use when documents are rejected or queries behave oddly."),
    E("PUT", "/{index}/_mapping", "Indices", "Update mapping",
      "Adds new fields to the mapping. Existing fields generally cannot "
      "change type — changing a field requires reindexing."),
    E("GET", "/{index}/_mapping/field/{fields}", "Indices", "Get field mapping",
      "Mapping for specific fields only (comma-separated, wildcards allowed), "
      "across all indices that contain them."),
    E("GET", "/{index}/_settings", "Indices", "Get index settings",
      "Current settings: shard/replica counts, refresh interval, allocation "
      "rules, write blocks. Check here when an index is stuck read-only."),
    E("PUT", "/{index}/_settings", "Indices", "Update index settings",
      "Changes dynamic settings at runtime, e.g. "
      "`{\"number_of_replicas\": 1}` or `{\"index.refresh_interval\": \"30s\"}`. "
      "Static settings (like shard count) require reindexing instead."),
    E("GET", "/{index}/_stats", "Indices", "Index statistics",
      "Docs, store bytes, indexing/merge/get/search operation counts and "
      "timings, segment counts and caches."),
    E("GET", "/{index}/_segments", "Indices", "Segment detail",
      "Per-shard Lucene segments: count, size, memory. Many tiny segments "
      "suggest merge pressure; consider force-merge on write-closed indices."),
    E("GET", "/{index}/_recovery", "Indices", "Recovery progress",
      "Shard recoveries for the index (replica rebuilds, relocations, "
      "restores) with per-stage progress."),
    E("POST", "/{index}/_cache/clear", "Indices", "Clear caches",
      "Drops query/request/fielddata caches for the index — a remedy for "
      "heap pressure caused by cached queries."),
    E("POST", "/{index}/_refresh", "Indices", "Refresh index",
      "Makes documents written since the last refresh visible to search. "
      "Normally automatic (1s); useful after bulk loads."),
    E("POST", "/{index}/_flush", "Indices", "Flush index",
      "Moves the transaction log into on-disk segments and starts a new "
      "translog. Heavier I/O than refresh; useful before snapshots."),
    E("POST", "/{index}/_forcemerge", "Indices", "Force merge",
      "**Maintenance.** Rewrites shards into `max_num_segments` segments. "
      "Best on indices that no longer receive writes."),
    E("POST", "/{index}/_clone/{target}", "Indices", "Clone index",
      "Creates `target` as a point-in-time copy of this index. The index "
      "must be read-only first (add a write block)."),
    E("POST", "/{index}/_shrink/{target}", "Indices", "Shrink index",
      "Creates `target` with fewer primary shards from this index — the "
      "remedy for *I created it with too many shards*. Index must be "
      "read-only and shard count must divide evenly."),
    E("POST", "/{index}/_split/{target}", "Indices", "Split index",
      "Creates `target` with more primary shards (multiply the original "
      "count) from this read-only index."),
    E("POST", "/{index}/_rollover", "Indices", "Rollover alias / data stream",
      "When `index` is an alias or data stream, creates the next backing "
      "index and switches writes to it. The backbone of time-based index "
      "management."),
    E("PUT", "/{index}/_alias/{name}", "Indices", "Add alias",
      "Adds alias `name` to the index. Aliases decouple applications from "
      "physical index names — the foundation of zero-downtime reindexing."),
    E("GET", "/{index}/_alias", "Indices", "Get aliases of index",
      "Lists aliases pointing at this index."),
    E("GET", "/_alias", "Indices", "Get all aliases",
      "Every alias in the cluster with the indices it points to."),
    E("GET", "/_alias/{name}", "Indices", "Get alias",
      "One alias (name or wildcard) and its target indices."),
    E("DELETE", "/{index}/_alias/{name}", "Indices", "Remove alias",
      "Removes the alias from the index (the index itself is untouched)."),
    E("HEAD", "/_alias/{name}", "Indices", "Check alias exists",
      "Existence check for an alias: 200 or 404."),
    E("POST", "/{index}/_analyze", "Indices", "Analyze text",
      "Runs text through an analyzer (or an ad-hoc chain of tokenizers and "
      "filters) and returns the produced tokens. The tool for debugging "
      "*why does my query not match?*"),
    E("GET", "/{index}/_analyze", "Indices", "Analyze text (GET)",
      "Same as the POST variant for simple cases where the text fits in the "
      "URL."),
    E("GET", "/{index}/_disk_usage", "Indices", "Disk usage per field",
      "Analyzes on-disk space per field (requires `run_expensive_tasks=true`). "
      "Shows which fields eat the disk."),
    E("GET", "/{index}/_field_usage_stats", "Indices", "Field usage stats",
      "How often each field was used (searched, aggregated, fetched) since "
      "last refresh — helps find unused fields worth removing."),
    E("GET", "/_resolve/index/{name}", "Indices", "Resolve index / alias / data stream",
      "Expands a name or wildcard into the concrete indices, aliases and "
      "data streams it matches — clarifies what a pattern actually hits."),
    E("PUT", "/{index}/_block/{block}", "Indices", "Add index block",
      "Adds a write/read/metadata block to the index, e.g. "
      "`write` to make it read-only before a clone or shrink."),
    E("GET", "/{index}/_shard_stores", "Indices", "On-disk shard copies",
      "Every physical shard copy for the index, its node, and store status "
      "(`used`, `unused`, `corrupt`)."),
    E("GET", "/_dangling", "Indices", "List dangling indices",
      "Indices whose data exists on a node but which are absent from the "
      "cluster state — typically after restoring data dirs or losing the "
      "master's state. They hold recoverable data."),
    E("POST", "/_dangling/{index_uuid}", "Indices", "Import dangling index",
      "Adopts a dangling index into the cluster, making it searchable again."),
    E("DELETE", "/_dangling/{index_uuid}", "Indices", "Delete dangling index",
      "**Destructive.** Discards a dangling index's data permanently."),
    E("POST", "/_cache/clear", "Indices", "Clear caches (cluster-wide)",
      "Clears caches across all indices — heavier than the per-index variant."),
]
