"""Registry entries: platform APIs — license, x-pack, CCR, ingest, misc."""

from .core import E

ENTRIES = [
    # ------------------------------ Licensing ------------------------------
    E("GET", "/_license", "Licensing", "Get license",
      "The current license: tier (basic/gold/platinum/enterprise), issue and "
      "expiry dates, and feature availability."),
    E("PUT", "/_license", "Licensing", "Install license",
      "Applies a license JSON obtained from Elastic."),
    E("DELETE", "/_license", "Licensing", "Delete license",
      "Reverts the cluster to basic license features."),
    E("GET", "/_license/trial_status", "Licensing", "Trial eligibility",
      "Whether the cluster is still eligible to start a self-managed trial."),
    E("POST", "/_license/start_trial", "Licensing", "Start trial",
      "Starts a 30-day trial of paid features (`acknowledge=true` required)."),
    E("POST", "/_license/start_basic", "Licensing", "Start basic",
      "Downgrades to the free basic license (`acknowledge=true` required)."),

    # --------------------------- X-Pack & platform -------------------------
    E("GET", "/_xpack", "Platform & X-Pack", "X-Pack info",
      "Which X-Pack features are available and enabled in the cluster."),
    E("GET", "/_xpack/usage", "Platform & X-Pack", "X-Pack usage",
      "Which X-Pack features are actually being used (ML jobs, ILM policies, "
      "security on/off…) — useful for capacity and license reviews."),
    E("GET", "/_features", "Platform & X-Pack", "List features",
      "System-managed features (each owns system indices) — context before "
      "any system-index maintenance."),
    E("POST", "/_features/_reset", "Platform & X-Pack", "Reset features",
      "**Destructive.** Deletes and recreates the system indices of the "
      "named features."),
    E("GET", "/_migration/deprecations", "Platform & X-Pack", "Upgrade deprecations",
      "Scans the cluster for settings/APIs/fields deprecated in the next "
      "major version — run before every upgrade."),
    E("POST", "/_monitoring/bulk", "Platform & X-Pack", "Monitoring bulk",
      "Ingests monitoring documents into the cluster (used by Metricbeat "
      "and legacy monitoring agents)."),

    # ------------------------------ Ingest ---------------------------------
    E("PUT", "/_ingest/pipeline/{id}", "Ingest", "Create/replace pipeline",
      "Defines a chain of ingest processors (grok, date, geoip, set…) "
      "applied to documents before indexing."),
    E("GET", "/_ingest/pipeline", "Ingest", "List pipelines",
      "All ingest pipelines with their processor definitions."),
    E("GET", "/_ingest/pipeline/{id}", "Ingest", "Get pipeline",
      "One pipeline's processor chain."),
    E("DELETE", "/_ingest/pipeline/{id}", "Ingest", "Delete pipeline",
      "Removes the pipeline."),
    E("POST", "/_ingest/pipeline/_simulate", "Ingest", "Simulate pipeline",
      "Runs sample documents through a pipeline (ad-hoc or stored) and shows "
      "the before/after — the dry-run for ingest logic."),
    E("POST", "/_ingest/pipeline/{id}/_simulate", "Ingest", "Simulate stored pipeline",
      "Simulates an already-stored pipeline."),
    E("GET", "/_ingest/processor/grok", "Ingest", "Grok patterns",
      "The built-in grok patterns available to the grok processor."),
    E("GET", "/_ingest/geoip/stats", "Ingest", "GeoIP statistics",
      "GeoIP database download status and cache sizes."),

    # --------------------- Cross-Cluster Replication -----------------------
    E("PUT", "/_ccr/auto_follow/{name}", "Cross-Cluster Replication", "Create auto-follow pattern",
      "Automatically follows new indices matching a pattern on a remote "
      "cluster (leader → follower replication)."),
    E("GET", "/_ccr/auto_follow", "Cross-Cluster Replication", "List auto-follow patterns",
      "All auto-follow patterns and the indices they have followed."),
    E("DELETE", "/_ccr/auto_follow/{name}", "Cross-Cluster Replication", "Delete auto-follow pattern",
      "Stops auto-following (existing follower indices keep replicating)."),
    E("PUT", "/{index}/_ccr/follow", "Cross-Cluster Replication", "Follow index",
      "Starts replicating a leader index from a remote cluster into this "
      "follower index."),
    E("POST", "/{index}/_ccr/pause_follow", "Cross-Cluster Replication", "Pause follow",
      "Temporarily halts replication for a follower index."),
    E("POST", "/{index}/_ccr/resume_follow", "Cross-Cluster Replication", "Resume follow",
      "Resumes paused replication."),
    E("POST", "/{index}/_ccr/unfollow", "Cross-Cluster Replication", "Unfollow index",
      "Fully detaches the follower from its leader (index must be closed)."),
    E("GET", "/_ccr/stats", "Cross-Cluster Replication", "CCR statistics",
      "Cluster-wide replication stats: follower/leader operations and read "
      "lags."),
    E("GET", "/{index}/_ccr/stats", "Cross-Cluster Replication", "Follow stats (index)",
      "Replication lag and error state for a follower index."),
    E("POST", "/{index}/_ccr/forget_follower", "Cross-Cluster Replication",
      "Forget follower shard",
      "Removes follower-shard metadata from a leader so replication can be "
      "cleanly retired."),

    # ------------------------------- Synonyms ------------------------------
    # (Synonym APIs require Elasticsearch 8.10+.)
    E("PUT", "/_synonyms/{id}", "Synonyms", "Create/replace synonym set",
      "Stores a synonym ruleset used by synonym token filters in analyzers "
      "and search-time query expansion."),
    E("GET", "/_synonyms", "Synonyms", "List synonym sets",
      "All stored synonym sets."),
    E("GET", "/_synonyms/{id}", "Synonyms", "Get synonym set",
      "One synonym set's rules."),
    E("DELETE", "/_synonyms/{id}", "Synonyms", "Delete synonym set",
      "Removes the synonym set."),
    E("PUT", "/_synonyms/{set_id}/{rule_id}", "Synonyms", "Create synonym rule",
      "Adds a single rule to a synonym set without replacing the whole set."),
    E("GET", "/_synonyms/{set_id}/{rule_id}", "Synonyms", "Get synonym rule",
      "One rule within a synonym set."),
    E("DELETE", "/_synonyms/{set_id}/{rule_id}", "Synonyms", "Delete synonym rule",
      "Removes one rule from a synonym set."),

    # ----------------------------- Query rules -----------------------------
    # (Query rules APIs require Elasticsearch 8.10+.)
    E("PUT", "/_query_rules/{ruleset_id}", "Query Rules", "Create/replace ruleset",
      "Defines curated query rules (pin/pexclude results for matching "
      "criteria) used by search applications for merchandising or "
      "curation."),
    E("GET", "/_query_rules", "Query Rules", "List rulesets",
      "All query rulesets."),
    E("GET", "/_query_rules/{ruleset_id}", "Query Rules", "Get ruleset",
      "One ruleset's rules."),
    E("DELETE", "/_query_rules/{ruleset_id}", "Query Rules", "Delete ruleset",
      "Removes the ruleset."),

    # -------------------------- Search applications ------------------------
    E("PUT", "/_application/search_application/{name}", "Search Applications",
      "Create/replace search application",
      "Defines a named search application wrapping an index (or data stream) "
      "with an optional query template."),
    E("GET", "/_application/search_application", "Search Applications",
      "List search applications",
      "All search applications."),
    E("GET", "/_application/search_application/{name}", "Search Applications",
      "Get search application",
      "One search application's definition."),
    E("DELETE", "/_application/search_application/{name}", "Search Applications",
      "Delete search application",
      "Removes the search application (underlying indices are kept)."),
    E("POST", "/_application/search_application/{name}/_render_query", "Search Applications",
      "Render search application query",
      "Renders the application's query template with parameters — shows "
      "exactly what will be executed."),
]
