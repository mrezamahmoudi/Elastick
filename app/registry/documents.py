"""Registry entries: document (CRUD) APIs (raw ES paths)."""

from .core import E

ENTRIES = [
    E("PUT", "/{index}/_doc/{id}", "Documents", "Index (create/replace) document",
      "Creates or fully replaces the document with the given ID. Every "
      "replace re-indexes the whole document — for partial changes use "
      "update instead."),
    E("POST", "/{index}/_doc", "Documents", "Index document (auto ID)",
      "Indexes a document letting Elasticsearch generate the ID."),
    E("PUT", "/{index}/_create/{id}", "Documents", "Create document (must be new)",
      "Creates the document only if the ID does not already exist; fails "
      "with 409 otherwise."),
    E("POST", "/{index}/_create/{id}", "Documents", "Create document (POST form)",
      "Same as the PUT variant — create-only semantics."),
    E("GET", "/{index}/_doc/{id}", "Documents", "Get document",
      "Fetches a document by ID (add `_source_includes`/`excludes` params to "
      "trim). 404 if absent."),
    E("HEAD", "/{index}/_doc/{id}", "Documents", "Check document exists",
      "Existence check: 200 or 404, no body."),
    E("GET", "/{index}/_source/{id}", "Documents", "Get document source",
      "Returns just the `_source` (the stored document), without metadata."),
    E("HEAD", "/{index}/_source/{id}", "Documents", "Check source exists",
      "Existence check for the document's source."),
    E("GET", "/_mget", "Documents", "Multi-get (GET)",
      "Fetches many documents in one call, possibly from different indices."),
    E("POST", "/_mget", "Documents", "Multi-get",
      "Fetches many documents in one call; the body lists `docs` with index, "
      "_id and optional _source filtering. Far cheaper than N single gets."),
    E("POST", "/{index}/_update/{id}", "Documents", "Update document",
      "Partial update: `doc` fields are merged in; supports scripted updates, "
      "upserts, and retry_on_conflict for version clashes."),
    E("POST", "/_bulk", "Documents", "Bulk (cluster-wide)",
      "The high-throughput write API. Body is **NDJSON**: an action line "
      "(index/create/update/delete) followed by a source line, e.g. "
      "`{\"index\": {\"_index\": \"i\"}}\n{\"field\": 1}\n`. Send with "
      "Content-Type `application/x-ndjson`."),
    E("POST", "/{index}/_bulk", "Documents", "Bulk (single index)",
      "Bulk writes where the index is given in the URL instead of each "
      "action line. Body is NDJSON."),
    E("DELETE", "/{index}/_doc/{id}", "Documents", "Delete document",
      "Deletes a document by ID. Deletes are soft: the doc is marked deleted "
      "and purged at the next segment merge."),
    E("POST", "/{index}/_delete_by_query", "Documents", "Delete by query",
      "**Destructive.** Deletes every document matching the query in the "
      "body. Runs as a background task; check progress in `/tasks`."),
    E("POST", "/{index}/_update_by_query", "Documents", "Update by query",
      "Re-indexes (or applies a script to) every matching document. Commonly "
      "used after mapping changes to pick up new fields."),
    E("POST", "/_reindex", "Documents", "Reindex",
      "Copies documents from a source index (or remote cluster) to a "
      "destination, optionally transforming them with a script. The standard "
      "way to change mappings or shard counts of existing data."),
    E("POST", "/_reindex/{task_id}/_rethrottle", "Documents", "Reindex rethrottle",
      "Changes the requests-per-second throttle of a running reindex task "
      "(set -1 for unlimited)."),
    E("POST", "/{index}/_count", "Documents", "Count documents",
      "Number of documents matching an optional query in the body."),
    E("GET", "/{index}/_count", "Documents", "Count documents (GET)",
      "Same count with the query passed via the `q` URL parameter."),
    E("GET", "/_count", "Documents", "Count documents (all indices)",
      "Document count across the whole cluster."),
    E("POST", "/_count", "Documents", "Count documents (all indices, body)",
      "Document count across the whole cluster with a query in the body."),
    E("GET", "/{index}/_explain/{id}", "Documents", "Explain match (GET)",
      "Why does this document match (or not match) the query in `q`? Shows "
      "the score decomposition per field."),
    E("POST", "/{index}/_explain/{id}", "Documents", "Explain match",
      "Full score explanation of one document against a query supplied in "
      "the body — the tool for relevance debugging."),
]
