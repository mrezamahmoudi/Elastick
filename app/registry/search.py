"""Registry entries: search-related APIs (raw ES paths)."""

from .core import E

ENTRIES = [
    E("GET", "/_search", "Search", "Search (all indices)",
      "Runs a search across every index; the query DSL body is identical to "
      "the POST variant."),
    E("POST", "/_search", "Search", "Search (all indices, body)",
      "Full search API: query DSL, aggregations, sort, pagination, "
      "highlighting, `_source` filtering. The core Elasticsearch endpoint."),
    E("GET", "/{index}/_search", "Search", "Search (GET)",
      "Search with the query expressed via URL parameters (`q`, `size`, "
      "`from`…). Handy for quick checks from curl."),
    E("POST", "/{index}/_search", "Search", "Search",
      "Search one index or pattern with the full query DSL in the body: "
      "`{\"query\": {...}, \"aggs\": {...}, \"size\": 10}`."),
    E("GET", "/{index}/_validate/query", "Search", "Validate query (GET)",
      "Checks whether a query is syntactically valid; add `explain=true` for "
      "the failure reason. First stop for *this query returns 400*."),
    E("POST", "/{index}/_validate/query", "Search", "Validate query",
      "Validates a query DSL body and optionally explains why it fails."),
    E("GET", "/_search/scroll", "Search", "Scroll (continue)",
      "Retrieves the next batch of results from an existing scroll context "
      "(pass `scroll_id` in the body)."),
    E("POST", "/_search/scroll", "Search", "Scroll (continue / start)",
      "Scrolling: take a snapshot of matching documents and walk through it "
      "in batches. Designed for exporting data, not for interactive paging."),
    E("DELETE", "/_search/scroll", "Search", "Clear scrolls (explicit list)",
      "Aborts specific scroll contexts listed in the body."),
    E("DELETE", "/_search/scroll/_all", "Search", "Clear all scrolls",
      "Aborts every scroll context in the cluster — use when stale scrolls "
      "are holding heap."),
    E("DELETE", "/_search/scroll/{scroll_id}", "Search", "Clear one scroll",
      "Aborts a single scroll context."),
    E("POST", "/_msearch", "Search", "Multi search",
      "Runs many searches in one request. Body is NDJSON: a header line per "
      "search followed by its body. One round trip for dashboards firing "
      "many queries."),
    E("POST", "/{index}/_msearch", "Search", "Multi search (single index)",
      "Multi search where the index is fixed in the URL."),
    E("POST", "/_search/template", "Search", "Search with template",
      "Runs a stored search template with parameters — keeps query logic in "
      "Elasticsearch and lets clients pass values."),
    E("POST", "/{index}/_search/template", "Search", "Search with template (single index)",
      "Templated search restricted to an index or pattern."),
    E("POST", "/_render/template", "Search", "Render search template",
      "Renders a mustache search template with the given params and returns "
      "the resulting search body — a dry-run for template debugging."),
    E("POST", "/_msearch/template", "Search", "Multi search with templates",
      "Multi search where each search uses a stored template."),
    E("GET", "/{index}/_termvectors/{id}", "Search", "Term vectors",
      "Returns the terms and statistics stored for one document's field — "
      "the internals behind scoring and highlighting."),
    E("POST", "/{index}/_termvectors/{id}", "Search", "Term vectors (POST)",
      "Term vectors for one document, optionally computing them on the fly "
      "for artificial documents."),
    E("GET", "/{index}/_mtermvectors", "Search", "Multi term vectors (GET)",
      "Term vectors for several documents at once."),
    E("POST", "/{index}/_mtermvectors", "Search", "Multi term vectors",
      "Term vectors for several documents in one request."),
    E("GET", "/_field_caps", "Search", "Field capabilities",
      "Which types and capabilities each field has across all indices."),
    E("GET", "/{index}/_field_caps", "Search", "Field capabilities (indices)",
      "Field capabilities restricted to an index or pattern."),
    E("POST", "/_rank_eval", "Search", "Rank evaluation",
      "Scores search quality against a labeled set of queries and expected "
      "results, with metrics like precision@k and reciprocal rank. For "
      "tuning relevance systematically."),
    E("POST", "/{index}/_rank_eval", "Search", "Rank evaluation (indices)",
      "Rank evaluation restricted to an index or pattern."),
    E("GET", "/_search_shards", "Search", "Search shards (all indices)",
      "Which shards a search against all indices would hit — helps reason "
      "about routing and fan-out."),
    E("GET", "/{index}/_search_shards", "Search", "Search shards",
      "Which shards a search on this index would target, and the nodes they "
      "live on."),
    E("POST", "/{index}/_pit", "Search", "Open point in time",
      "Opens a lightweight, consistent view of the index for pagination "
      "(pass `keep_alive`, e.g. `1m`). The modern replacement for scroll in "
      "search-after pagination."),
    E("DELETE", "/_pit", "Search", "Close point in time",
      "Closes point-in-time contexts listed in the body, releasing their "
      "resources."),
]
