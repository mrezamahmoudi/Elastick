"""Registry entries: the complete `_cat` API family (raw ES paths).

Every `_cat` endpoint returns compact tabular data; this service always
requests `format=json` (unless the caller overrides it) so responses render
properly in Swagger UI.
"""

from .core import E

ENTRIES = [
    E("GET", "/_cat", "Cat APIs", "Cat help",
      "Lists every available `_cat` endpoint with its columns — the menu of "
      "everything below."),
    E("GET", "/_cat/aliases", "Cat APIs", "Aliases",
      "One row per alias: the indices it points to, its filter and routing. "
      "Spot orphaned or mis-pointed aliases quickly."),
    E("GET", "/_cat/aliases/{alias}", "Cat APIs", "Aliases (pattern)",
      "Alias table filtered by name or wildcard pattern."),
    E("GET", "/_cat/allocation", "Cat APIs", "Disk allocation",
      "Disk used/free/percent and shard count per node. Watch for nodes "
      "drifting above the 85% low watermark."),
    E("GET", "/_cat/allocation/{node_id}", "Cat APIs", "Disk allocation (nodes)",
      "Allocation table filtered to specific nodes."),
    E("GET", "/_cat/component_templates", "Cat APIs", "Component templates",
      "Composable component templates with their version and content."),
    E("GET", "/_cat/count", "Cat APIs", "Document count",
      "Document count per index — a fast sanity check that data is arriving."),
    E("GET", "/_cat/count/{index}", "Cat APIs", "Document count (pattern)",
      "Document counts for indices matching a pattern."),
    E("GET", "/_cat/fielddata", "Cat APIs", "Fielddata memory",
      "Heap used by fielddata per node and field. Large values here are a "
      "classic heap-pressure source."),
    E("GET", "/_cat/fielddata/{fields}", "Cat APIs", "Fielddata memory (fields)",
      "Fielddata table filtered to specific fields."),
    E("GET", "/_cat/health", "Cat APIs", "Health",
      "One-row cluster health: status, total/active shards, pending tasks, "
      "uptime. The 5-second *is anything wrong?* check."),
    E("GET", "/_cat/indices", "Cat APIs", "Indices",
      "One row per index: health, status, docs, deleted docs, store size, "
      "primary size."),
    E("GET", "/_cat/indices/{index}", "Cat APIs", "Indices (pattern)",
      "Index table filtered by name or wildcard."),
    E("GET", "/_cat/master", "Cat APIs", "Master node",
      "Which node is currently the elected master."),
    E("GET", "/_cat/nodeattrs", "Cat APIs", "Node attributes",
      "Custom attributes per node (e.g. `rack`, `zone`) used in allocation "
      "filtering rules."),
    E("GET", "/_cat/nodes", "Cat APIs", "Nodes",
      "One row per node: roles, CPU, heap, disk, load, uptime. The "
      "at-a-glance fleet view."),
    E("GET", "/_cat/pending_tasks", "Cat APIs", "Pending tasks",
      "Queued cluster-state tasks with their priority and wait time."),
    E("GET", "/_cat/plugins", "Cat APIs", "Plugins",
      "Plugins installed on each node — verify all nodes run the same "
      "plugin set after upgrades."),
    E("GET", "/_cat/recovery", "Cat APIs", "Recovery",
      "Shard recovery progress per index: stage, bytes and files transferred."),
    E("GET", "/_cat/recovery/{index}", "Cat APIs", "Recovery (pattern)",
      "Recovery table filtered by index pattern."),
    E("GET", "/_cat/repositories", "Cat APIs", "Snapshot repositories",
      "Registered snapshot repositories and their types."),
    E("GET", "/_cat/segments", "Cat APIs", "Segments",
      "One row per shard's segment set: count, memory, sizes."),
    E("GET", "/_cat/segments/{index}", "Cat APIs", "Segments (pattern)",
      "Segment table filtered by index pattern."),
    E("GET", "/_cat/shards", "Cat APIs", "Shards",
      "One row per shard copy: index, shard, primary/replica, state, node, "
      "size. Anything not `STARTED` deserves a look."),
    E("GET", "/_cat/shards/{index}", "Cat APIs", "Shards (pattern)",
      "Shard table filtered by index pattern."),
    E("GET", "/_cat/snapshots/{repository}", "Cat APIs", "Snapshots",
      "Snapshots in a repository with start/end times and state."),
    E("GET", "/_cat/tasks", "Cat APIs", "Tasks",
      "Running tasks with action, start time and running time."),
    E("GET", "/_cat/templates", "Cat APIs", "Templates",
      "Index templates (legacy and composable) with their order/patterns."),
    E("GET", "/_cat/thread_pool", "Cat APIs", "Thread pools",
      "Active/queue/rejected counts per node and pool. `rejected > 0` is "
      "the first symptom of overload."),
    E("GET", "/_cat/thread_pool/{thread_pool_patterns}", "Cat APIs", "Thread pools (pattern)",
      "Thread-pool table filtered to specific pools, e.g. `search,write`."),
    E("GET", "/_cat/ml/anomaly_detectors", "Cat APIs", "ML anomaly detectors",
      "ML anomaly detection jobs with state, model size and data counts."),
    E("GET", "/_cat/ml/datafeeds", "Cat APIs", "ML datafeeds",
      "ML datafeeds with state and the jobs they feed."),
    E("GET", "/_cat/ml/data_frame/analytics", "Cat APIs", "ML data frame analytics",
      "Data frame analytics jobs with state and progress."),
    E("GET", "/_cat/ml/trained_models", "Cat APIs", "ML trained models",
      "Trained models with size, ingest usage and deployment state."),
    E("GET", "/_cat/transforms", "Cat APIs", "Transforms",
      "Transforms with state, checkpoint progress and documents processed."),
    E("GET", "/_cat/transforms/{transform_id}", "Cat APIs", "Transforms (pattern)",
      "Transform table filtered by transform ID."),
]
