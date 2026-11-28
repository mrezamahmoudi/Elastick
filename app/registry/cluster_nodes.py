"""Registry entries: cluster-level and node-level APIs (raw ES paths)."""

from .core import E

ENTRIES = [
    # ----------------------------- Cluster ---------------------------------
    E("GET", "/_cluster/health", "Cluster", "Cluster health",
      "Overall cluster status: green (everything allocated), yellow (a replica "
      "is missing) or red (a primary shard is missing). Supports "
      "`level=indices|shards` for drill-down and `wait_for_status` to block "
      "until a target status is reached."),
    E("GET", "/_cluster/health/{index}", "Cluster", "Health of specific indices",
      "Same as cluster health but restricted to the given index or wildcard "
      "pattern — answers *is this index's shard set complete?*"),
    E("GET", "/_cluster/pending_tasks", "Cluster", "Pending cluster-state tasks",
      "Lists cluster-state changes queued on the master with the time each has "
      "waited. A growing queue signals master overload."),
    E("GET", "/_cluster/state", "Cluster", "Cluster state (full)",
      "The complete internal metadata distributed by the master: routing "
      "tables, index metadata, node membership. Very verbose — filter with "
      "`metric` and `index` when possible."),
    E("GET", "/_cluster/state/{metric}", "Cluster", "Cluster state (one metric)",
      "A single block of the cluster state, e.g. `routing_table` or "
      "`metadata`. Use to inspect one aspect without the full payload."),
    E("GET", "/_cluster/state/{metric}/{index}", "Cluster", "Cluster state (metric + index)",
      "A single cluster-state metric restricted to one index or pattern."),
    E("GET", "/_cluster/stats", "Cluster", "Cluster statistics",
      "Cluster-wide numbers: document and byte counts, heap per node, field "
      "and mapping counts, node versions. The capacity-planning endpoint."),
    E("GET", "/_cluster/stats/nodes/{node_id}", "Cluster", "Cluster statistics (node subset)",
      "Cluster statistics computed over a subset of nodes."),
    E("GET", "/_cluster/settings", "Cluster", "Get cluster settings",
      "Shows persistent and transient cluster settings (watermarks, "
      "allocation enablement, throttling). Add `include_defaults=true` to see "
      "built-in defaults too."),
    E("PUT", "/_cluster/settings", "Cluster", "Update cluster settings",
      "**Changes cluster behavior.** Updates persistent or transient settings, "
      "e.g. `{\"persistent\": {\"cluster.routing.allocation.enable\": \"primaries\"}}`. "
      "Pass `null` for a setting to reset it to its default."),
    E("POST", "/_cluster/reroute", "Cluster", "Reroute shards manually",
      "**Advanced.** Explicitly allocate, move or cancel shards via commands "
      "in the body. Use `dry_run=true` (the safe default in Swagger) to "
      "validate commands without applying them."),
    E("GET", "/_cluster/allocation/explain", "Shards & Allocation",
      "Explain shard allocation",
      "Asks the cluster why the first unassigned shard it finds is not "
      "allocated — the definitive diagnostic for red/yellow clusters."),
    E("POST", "/_cluster/allocation/explain", "Shards & Allocation",
      "Explain a specific shard",
      "Same explanation, but for a shard you name in the body: "
      "`{\"index\": \"i\", \"shard\": 0, \"primary\": true}`. Also explains "
      "why an *assigned* shard cannot move or remain where it is."),
    E("GET", "/_remote/info", "Cluster", "Remote cluster connections",
      "Lists configured remote clusters (for cross-cluster search/replication) "
      "and their connection health."),
    E("GET", "/_cluster/voting_config_exclusions", "Cluster", "Voting config exclusions (list)",
      "Shows nodes excluded from the master voting configuration — typically "
      "set deliberately before decommissioning master-eligible nodes."),
    E("POST", "/_cluster/voting_config_exclusions", "Cluster", "Add voting config exclusions",
      "**Cluster-topology sensitive.** Excludes master-eligible nodes from the "
      "voting configuration, e.g. before permanently removing them. Misuse can "
      "prevent master election."),
    E("DELETE", "/_cluster/voting_config_exclusions", "Cluster", "Clear voting config exclusions",
      "Removes voting-config exclusions (all of them, or only those matching "
      "`node_ids`/`node_names`), re-admitting the nodes to master elections."),
    E("GET", "/_health_report", "Cluster", "Health report (component health)",
      "New-style health report: per-component indicators (master, repository, "
      "slm…) with `green/yellow/red` status, impacts and remediation hints. "
      "More actionable than raw cluster health for diagnosis. "
      "(Requires Elasticsearch 8.11+; older versions return 400.)"),

    # ------------------------------ Nodes ----------------------------------
    E("GET", "/_nodes", "Nodes", "Node information",
      "Every node's identity, roles, version, uptime, settings and plugins. "
      "First check for *who is in the cluster* and version/role anomalies."),
    E("GET", "/_nodes/{node_id}", "Nodes", "Node information (subset)",
      "Node information filtered to specific nodes by name/ID or wildcard, "
      "e.g. `es-data-*`."),
    E("GET", "/_nodes/stats", "Nodes", "Node statistics",
      "Live per-node metrics: JVM heap/GC, indexing and search throughput, "
      "merges, filesystem, transport, thread pools, circuit breakers. The "
      "workhorse for *why is this node struggling?*"),
    E("GET", "/_nodes/{node_id}/stats", "Nodes", "Node statistics (subset)",
      "Node statistics filtered to specific nodes; add `metric` to limit "
      "groups (e.g. `jvm,os,fs,thread_pool`)."),
    E("GET", "/_nodes/usage", "Nodes", "Node API usage",
      "How many times each REST API has been called per node since restart. "
      "Curiosity more than health."),
    E("GET", "/_nodes/{node_id}/usage", "Nodes", "Node API usage (subset)",
      "API usage filtered to specific nodes."),
    E("GET", "/_nodes/hot_threads", "Nodes", "Hot threads (all nodes)",
      "CPU-bound thread snapshots per node. If a node is pinned at 100% CPU, "
      "this shows which code path is responsible."),
    E("GET", "/_nodes/{node_id}/hot_threads", "Nodes", "Hot threads (subset)",
      "Hot-thread snapshots for specific nodes; tune `threads`, `interval` "
      "and `type` (`cpu`, `wait`, `block`, `mem`)."),
    E("POST", "/_nodes/{node_id}/reload_secure_settings", "Nodes", "Reload secure settings",
      "Re-reads keystore-backed secure settings (passwords, keys) from the "
      "keystore without restarting the node, e.g. after rotating repository "
      "credentials."),
    E("GET", "/_nodes/shutdown", "Nodes", "Node shutdown status",
      "Status of graceful node shutdowns in progress: which nodes are being "
      "shut down, what remains (shard moves, in-flight tasks). "
      "(Requires Elasticsearch 8.0+.)"),
    E("PUT", "/_nodes/{node_id}/shutdown", "Nodes", "Start graceful node shutdown",
      "Marks a node for graceful removal: the cluster drains its shards and "
      "waits for work to complete. Much safer than just stopping the process. "
      "(Requires Elasticsearch 8.0+.)"),
    E("DELETE", "/_nodes/{node_id}/shutdown", "Nodes", "Cancel node shutdown",
      "Cancels an in-progress graceful shutdown, returning the node to "
      "normal service. (Requires Elasticsearch 8.0+.)"),
]
