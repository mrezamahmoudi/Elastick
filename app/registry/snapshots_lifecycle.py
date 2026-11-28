"""Registry entries: snapshots, SLM, ILM, data streams and templates."""

from .core import E

ENTRIES = [
    # --------------------------- Snapshots ---------------------------------
    E("PUT", "/_snapshot/{repository}", "Snapshots & Recovery", "Create repository",
      "Registers a backup repository (filesystem, S3, GCS, Azure…) with its "
      "settings in the body. The prerequisite for every snapshot."),
    E("GET", "/_snapshot", "Snapshots & Recovery", "Get repositories",
      "Lists all registered repositories. Empty output means the cluster has "
      "no backups configured — a finding worth raising."),
    E("GET", "/_snapshot/{repository}", "Snapshots & Recovery", "Get repository",
      "One repository's type and settings."),
    E("DELETE", "/_snapshot/{repository}", "Snapshots & Recovery", "Delete repository",
      "Unregisters the repository (its data in the storage backend is not "
      "deleted unless `purge` semantics apply via the plugin)."),
    E("POST", "/_snapshot/{repository}/_verify", "Snapshots & Recovery", "Verify repository",
      "Confirms every node can reach the repository — the check to run after "
      "changing credentials or network paths."),
    E("POST", "/_snapshot/{repository}/_cleanup", "Snapshots & Recovery", "Repository cleanup",
      "Removes stale data left in the repository by failed or aborted "
      "snapshots, reclaiming space."),
    E("POST", "/_snapshot/{repository}/_analyze", "Snapshots & Recovery", "Repository analysis",
      "Runs a read/write performance test against the repository and reports "
      "throughput — use to validate a new backup target before relying on it."),
    E("PUT", "/_snapshot/{repository}/{snapshot}", "Snapshots & Recovery", "Create snapshot",
      "Snapshots the indices named in the body (or all). Add "
      "`wait_for_completion=true` for synchronous execution; otherwise track "
      "progress via the status endpoint."),
    E("GET", "/_snapshot/{repository}/{snapshot}", "Snapshots & Recovery", "Get snapshots",
      "Snapshot metadata: indices, start/end, state (`SUCCESS`, `FAILED`, "
      "`PARTIAL`, `IN_PROGRESS`). Supports wildcards."),
    E("DELETE", "/_snapshot/{repository}/{snapshot}", "Snapshots & Recovery", "Delete snapshot",
      "Deletes a snapshot and reclaims its unique data from the repository."),
    E("GET", "/_snapshot/{repository}/{snapshot}/_status", "Snapshots & Recovery", "Snapshot status",
      "Per-shard progress of a snapshot: files and bytes copied so far."),
    E("POST", "/_snapshot/{repository}/{snapshot}/_clone/{target_snapshot}", "Snapshots & Recovery",
      "Clone snapshot",
      "Creates `target_snapshot` sharing data files with the source — cheap "
      "copies for retention policies."),
    E("POST", "/_snapshot/{repository}/{snapshot}/_restore", "Snapshots & Recovery",
      "Restore snapshot",
      "**Data-changing.** Restores indices from the snapshot, optionally "
      "renamed (`rename_pattern`/`rename_replacement`) or partially "
      "(`indices`). Can also restore the cluster state."),
    E("POST", "/_snapshot/{repository}/{snapshot}/_mount", "Snapshots & Recovery",
      "Mount searchable snapshot",
      "Creates a new index backed directly by the snapshot's data files "
      "(fully or partially mounted) — data lives in the repository, not on "
      "local disks."),

    # ------------------------- Snapshot Lifecycle --------------------------
    E("PUT", "/_slm/policy/{policy_id}", "Snapshot Lifecycle (SLM)", "Create/replace SLM policy",
      "Defines an automatic snapshot schedule (cron), the indices to capture "
      "and the retention rules that prune old snapshots."),
    E("GET", "/_slm/policy", "Snapshot Lifecycle (SLM)", "Get SLM policies",
      "All snapshot lifecycle policies with their last execution and "
      "statistics."),
    E("GET", "/_slm/policy/{policy_id}", "Snapshot Lifecycle (SLM)", "Get SLM policy",
      "One policy's definition and execution history."),
    E("DELETE", "/_slm/policy/{policy_id}", "Snapshot Lifecycle (SLM)", "Delete SLM policy",
      "Removes the policy (existing snapshots are kept)."),
    E("POST", "/_slm/policy/{policy_id}/_execute", "Snapshot Lifecycle (SLM)",
      "Execute SLM policy now",
      "Triggers the policy immediately, outside its schedule — the manual "
      "*take a backup right now* button."),
    E("POST", "/_slm/_execute_retention", "Snapshot Lifecycle (SLM)", "Execute retention now",
      "Runs the retention cleanup immediately instead of waiting for its "
      "scheduled time."),
    E("GET", "/_slm/stats", "Snapshot Lifecycle (SLM)", "SLM statistics",
      "Retention runs, snapshot counts and per-policy execution stats."),
    E("POST", "/_slm/start", "Snapshot Lifecycle (SLM)", "Start SLM",
      "Resumes the snapshot lifecycle service after a stop."),
    E("POST", "/_slm/stop", "Snapshot Lifecycle (SLM)", "Stop SLM",
      "Halts all automatic snapshotting and retention. Usually stopped "
      "during major maintenance; remember to start it again."),
    E("GET", "/_slm/status", "Snapshot Lifecycle (SLM)", "SLM status",
      "Whether the SLM service is `RUNNING` or `STOPPED` — quick audit that "
      "backups are actually enabled."),

    # -------------------------- Index Lifecycle ----------------------------
    E("PUT", "/_ilm/policy/{policy_id}", "Index Lifecycle (ILM)", "Create/replace ILM policy",
      "Defines the lifecycle phases (hot → warm → cold → frozen → delete) "
      "and the actions in each (rollover, shrink, force merge, delete…)."),
    E("GET", "/_ilm/policy", "Index Lifecycle (ILM)", "Get ILM policies",
      "All lifecycle policies in the cluster."),
    E("GET", "/_ilm/policy/{policy_id}", "Index Lifecycle (ILM)", "Get ILM policy",
      "One policy's full phase/action definition."),
    E("DELETE", "/_ilm/policy/{policy_id}", "Index Lifecycle (ILM)", "Delete ILM policy",
      "Removes the policy; indices still referencing it keep their current "
      "step."),
    E("POST", "/_ilm/move/{index}", "Index Lifecycle (ILM)", "Move index to step",
      "**Advanced.** Manually advances (or rewinds) an index to a named "
      "lifecycle step — the fix for indices stuck in a failed step."),
    E("POST", "/_ilm/remove/{index}", "Index Lifecycle (ILM)", "Remove ILM from index",
      "Detaches lifecycle management from the index; it stops progressing "
      "through phases."),
    E("GET", "/_ilm/status", "Index Lifecycle (ILM)", "ILM status",
      "Whether ILM is `RUNNING` or `STOPPED` cluster-wide."),
    E("POST", "/_ilm/start", "Index Lifecycle (ILM)", "Start ILM",
      "Resumes lifecycle processing after a stop."),
    E("POST", "/_ilm/stop", "Index Lifecycle (ILM)", "Stop ILM",
      "Pauses all lifecycle processing (policies stay attached). Typical "
      "during maintenance windows."),
    E("GET", "/{index}/_ilm/explain", "Index Lifecycle (ILM)", "Explain index lifecycle",
      "Where this index stands in its lifecycle: current phase/action/step, "
      "and the error if it is stuck. The ILM troubleshooting endpoint."),
    E("POST", "/_ilm/migrate_to_data_tiers", "Index Lifecycle (ILM)", "Migrate to data tiers",
      "One-shot helper converting legacy node-role-based ILM setups to the "
      "data-tier model."),

    # ---------------------------- Data Streams -----------------------------
    E("PUT", "/_data_stream/{name}", "Data Streams", "Create data stream",
      "Creates an empty data stream (its backing index is created on first "
      "write). The name must match an index template."),
    E("DELETE", "/_data_stream/{name}", "Data Streams", "Delete data stream",
      "**Destructive.** Deletes the data stream and all of its backing "
      "indices."),
    E("GET", "/_data_stream", "Data Streams", "Get data streams",
      "All data streams with their backing indices, generation and timestamps."),
    E("GET", "/_data_stream/{name}", "Data Streams", "Get data stream",
      "One data stream (name or wildcard) and its backing indices."),
    E("GET", "/_data_stream/_stats", "Data Streams", "Data stream statistics",
      "Shard and byte counts per data stream."),
    E("GET", "/_data_stream/{name}/_stats", "Data Streams", "Data stream statistics (pattern)",
      "Statistics filtered to a data stream or wildcard."),
    E("POST", "/_data_stream/_migrate", "Data Streams", "Migrate alias to data stream",
      "Converts legacy index aliases into data streams."),
    E("POST", "/_data_stream/{name}/_rollover", "Data Streams", "Rollover data stream",
      "Creates the next backing index and switches writes to it."),
    E("POST", "/_data_stream/_modify", "Data Streams", "Modify data stream",
      "Manually adds or removes backing indices from a data stream — for "
      "repairing unusual situations, not routine use."),

    # -------------------------- Index Templates ----------------------------
    E("PUT", "/_index_template/{name}", "Index Templates", "Create/replace index template",
      "Defines a composable template: index patterns, composed of component "
      "templates, plus settings/mappings/aliases applied to new indices."),
    E("GET", "/_index_template", "Index Templates", "Get index templates",
      "All composable index templates."),
    E("GET", "/_index_template/{name}", "Index Templates", "Get index template",
      "One template's definition."),
    E("HEAD", "/_index_template/{name}", "Index Templates", "Check template exists",
      "Existence check for a template."),
    E("DELETE", "/_index_template/{name}", "Index Templates", "Delete index template",
      "Removes the template (existing indices are unaffected)."),
    E("POST", "/_index_template/_simulate_index/{name}", "Index Templates",
      "Simulate index from templates",
      "Given a would-be index name, returns the exact settings/mappings/"
      "aliases the matching templates would apply — the dry-run for template "
      "changes."),
    E("POST", "/_index_template/_simulate/{name}", "Index Templates",
      "Simulate template",
      "Shows what a specific template (optionally with an overriding body) "
      "would produce."),
    E("PUT", "/_component_template/{name}", "Index Templates", "Create/replace component template",
      "Defines a reusable building block (mappings/settings) that index "
      "templates compose."),
    E("GET", "/_component_template", "Index Templates", "Get component templates",
      "All component templates."),
    E("GET", "/_component_template/{name}", "Index Templates", "Get component template",
      "One component template's definition."),
    E("HEAD", "/_component_template/{name}", "Index Templates", "Check component template exists",
      "Existence check for a component template."),
    E("DELETE", "/_component_template/{name}", "Index Templates", "Delete component template",
      "Removes the component (fails if an index template still uses it)."),
    E("PUT", "/_template/{name}", "Index Templates", "Create/replace legacy template",
      "The pre-7.8 template style. Still works but composable templates "
      "(`_index_template`) take precedence when both match."),
    E("GET", "/_template", "Index Templates", "Get legacy templates",
      "All legacy index templates."),
    E("GET", "/_template/{name}", "Index Templates", "Get legacy template",
      "One legacy template's definition."),
    E("HEAD", "/_template/{name}", "Index Templates", "Check legacy template exists",
      "Existence check for a legacy template."),
    E("DELETE", "/_template/{name}", "Index Templates", "Delete legacy template",
      "Removes the legacy template."),
]
