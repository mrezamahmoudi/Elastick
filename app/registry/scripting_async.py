"""Registry entries: scripting, async search, SQL and EQL APIs."""

from .core import E

ENTRIES = [
    # ----------------------------- Scripting -------------------------------
    E("PUT", "/_scripts/{id}", "Scripting", "Create/replace stored script",
      "Stores a parameterized script (painless or mustache) under an ID for "
      "reuse in searches, updates and ingest pipelines."),
    E("GET", "/_scripts/{id}", "Scripting", "Get stored script",
      "Returns the stored script's source."),
    E("DELETE", "/_scripts/{id}", "Scripting", "Delete stored script",
      "Removes the stored script."),
    E("GET", "/_script_context", "Scripting", "Script contexts",
      "Lists the contexts scripts can run in (score, filter, ingest…), each "
      "with the variables available to the script."),
    E("GET", "/_script_language", "Scripting", "Script languages",
      "Installed scripting languages and their types/contexts."),
    E("POST", "/_scripts/painless/_execute", "Scripting", "Painless execute",
      "Runs a Painless snippet in a chosen context and returns the result — "
      "a scratchpad for testing scripts before deploying them."),

    # ---------------------------- Async Search -----------------------------
    E("POST", "/_async_search", "Async Search", "Submit async search (all indices)",
      "Starts a search that runs in the background and returns a handle "
      "immediately; poll it with the returned `id`. For long-running "
      "searches that would otherwise time out."),
    E("POST", "/{index}/_async_search", "Async Search", "Submit async search",
      "Async search restricted to an index or pattern."),
    E("GET", "/_async_search/{id}", "Async Search", "Get async search results",
      "Fetches current results for an async search; add `wait_for_completion_"
      "timeout` to block briefly for completion."),
    E("GET", "/_async_search/status/{id}", "Async Search", "Async search status",
      "Progress metadata (phase, shards completed) without the results."),
    E("DELETE", "/_async_search/{id}", "Async Search", "Delete async search",
      "Stops the search and removes its stored results."),

    # -------------------------------- SQL ----------------------------------
    E("POST", "/_sql", "SQL", "Run SQL query",
      "Executes an SQL `SELECT` against indices, e.g. "
      "`{\"query\": \"SELECT * FROM logs-* LIMIT 10\"}`. Columns map to "
      "mapped fields."),
    E("POST", "/_sql/close", "SQL", "Close SQL cursor",
      "Releases the resources behind a paginated SQL cursor."),
    E("GET", "/_sql/async/{id}", "SQL", "Get async SQL results",
      "Fetches results of an async SQL query; pass `cursor` for the next "
      "page."),
    E("GET", "/_sql/async/status/{id}", "SQL", "Async SQL status",
      "Progress of a running async SQL query."),
    E("DELETE", "/_sql/async/{id}", "SQL", "Delete async SQL",
      "Stops an async SQL query and drops its results."),
    E("POST", "/_sql/translate", "SQL", "Translate SQL to DSL",
      "Returns the equivalent Elasticsearch query DSL for an SQL statement — "
      "great for learning what your SQL actually does."),

    # -------------------------------- EQL ----------------------------------
    E("POST", "/{index}/_eql/search", "EQL", "EQL search",
      "Event Query Language search over sequence/event data (security "
      "analytics), e.g. finding event sequences matching a pattern."),
    E("GET", "/_eql/search/{id}", "EQL", "Get async EQL results",
      "Fetches results of an async EQL search."),
    E("GET", "/_eql/search/status/{id}", "EQL", "Async EQL status",
      "Execution status of one async EQL search."),
    E("DELETE", "/_eql/search/{id}", "EQL", "Delete async EQL",
      "Stops an async EQL search and removes its results."),
]
