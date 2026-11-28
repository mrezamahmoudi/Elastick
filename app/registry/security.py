"""Registry entries: security APIs (raw ES paths)."""

from .core import E

ENTRIES = [
    E("GET", "/_security/_authenticate", "Security", "Who am I?",
      "Returns the identity behind the current request's credentials: user, "
      "roles and authentication realm. The first call to make when "
      "debugging permission problems."),
    E("GET", "/_security/user", "Security", "List users",
      "All native users with their roles and enabled state."),
    E("GET", "/_security/user/{username}", "Security", "Get user",
      "One user's roles, full name, email and metadata."),
    E("PUT", "/_security/user/{username}", "Security", "Create/update user",
      "Creates a user (with password and roles in the body) or updates an "
      "existing one."),
    E("DELETE", "/_security/user/{username}", "Security", "Delete user",
      "Removes a native user."),
    E("POST", "/_security/user/{username}/_enable", "Security", "Enable user",
      "Re-enables a previously disabled user."),
    E("POST", "/_security/user/{username}/_disable", "Security", "Disable user",
      "Disables the user's credentials without deleting them — the gentle "
      "offboarding step."),
    E("PUT", "/_security/user/{username}/password", "Security", "Change password",
      "Sets a new password for the user."),
    E("GET", "/_security/role", "Security", "List roles",
      "All roles with their cluster/index/privilege definitions."),
    E("GET", "/_security/role/{role}", "Security", "Get role",
      "One role's full privilege definition."),
    E("PUT", "/_security/role/{role}", "Security", "Create/update role",
      "Creates or updates a role: cluster privileges, index privileges, "
      "run-as users and optional field/document-level security."),
    E("DELETE", "/_security/role/{role}", "Security", "Delete role",
      "Removes the role."),
    E("GET", "/_security/role_mapping", "Security", "List role mappings",
      "Rules mapping external identities (LDAP groups, SAML attributes…) to "
      "Elasticsearch roles."),
    E("GET", "/_security/role_mapping/{name}", "Security", "Get role mapping",
      "One role-mapping rule."),
    E("PUT", "/_security/role_mapping/{name}", "Security", "Create/update role mapping",
      "Defines or updates how external principals map to roles."),
    E("DELETE", "/_security/role_mapping/{name}", "Security", "Delete role mapping",
      "Removes a role-mapping rule."),
    E("GET", "/_security/privilege", "Security", "List privileges",
      "All application privileges defined in the cluster."),
    E("GET", "/_security/privilege/{application}", "Security", "Get privileges (application)",
      "Privileges of one application."),
    E("GET", "/_security/privilege/{application}/{name}", "Security", "Get privilege",
      "One named privilege of an application."),
    E("PUT", "/_security/privilege/{application}/{name}", "Security", "Create/update privilege",
      "Defines an application privilege (a named set of actions)."),
    E("DELETE", "/_security/privilege/{application}/{name}", "Security", "Delete privilege",
      "Removes an application privilege."),
    E("POST", "/_security/user/_has_privileges", "Security", "Has privileges (user)",
      "Checks whether a named user holds a list of cluster/index privileges "
      "— an authorization audit without logging in as them."),
    E("POST", "/_security/_has_privileges", "Security", "Has privileges (self)",
      "Checks the privileges of the *calling* user against the body's list."),
    E("POST", "/_security/api_key", "Security", "Create API key",
      "Issues an API key with a role descriptor and optional expiration. "
      "The response contains the key — copy it immediately, it is not "
      "retrievable later."),
    E("GET", "/_security/api_key", "Security", "Get API keys",
      "Lists API keys with validity and expiration; filter by id, name or "
      "owner."),
    E("DELETE", "/_security/api_key", "Security", "Invalidate API keys",
      "Revokes API keys listed in the body (by id or name). Revocation is "
      "the response to a suspected leak."),
    E("POST", "/_security/api_key/_query", "Security", "Query API keys",
      "Searches API keys with a query DSL body and pagination — scales where "
      "the plain list endpoint does not."),
    E("POST", "/_security/api_key/grant", "Security", "Grant API key",
      "Creates an API key on behalf of another user (service-account or "
      "access-token based delegation)."),
    E("POST", "/_security/oauth2/token", "Security", "Get access token",
      "Exchanges credentials (or a refresh token) for an OAuth2-style "
      "access token."),
    E("DELETE", "/_security/oauth2/token", "Security", "Invalidate access token",
      "Revokes an access or refresh token."),
    E("GET", "/_security/service", "Security", "List service accounts",
      "Built-in service accounts (e.g. `elastic/kibana`) available for "
      "service-to-service auth."),
    E("GET", "/_security/service/{namespace}/{service}/credential", "Security",
      "Get service account credentials",
      "The tokens currently issued for a service account."),
    E("POST", "/_security/service/{namespace}/{service}/credential/token/{token_name}",
      "Security", "Create service token",
      "Issues a new bearer token for a service account."),
    E("DELETE", "/_security/service/{namespace}/{service}/credential/token/{token_name}",
      "Security", "Delete service token",
      "Deletes a service-account token."),
    E("POST", "/_security/service/{namespace}/{service}/credential/_clear_cache",
      "Security", "Clear service-token cache",
      "Forces revalidation of cached service-account tokens on all nodes."),
    E("POST", "/_security/user/_clear_cache", "Security", "Clear user cache",
      "Drops cached user credentials/roles so changes (e.g. in LDAP) take "
      "effect immediately."),
    E("POST", "/_security/role/{role}/_clear_cache", "Security", "Clear role cache",
      "Drops the cached privilege set of a role."),
    E("GET", "/_ssl/certificates", "Security", "TLS certificates",
      "The TLS certificates the HTTP layer is serving, with expiry dates — "
      "a certificate-expiry audit in one call."),
    E("POST", "/_security/saml/prepare", "Security", "SAML prepare authentication",
      "Starts a SAML login: returns the redirect URL to the identity "
      "provider."),
    E("POST", "/_security/saml/authenticate", "Security", "SAML authenticate",
      "Consumes the IdP's SAML response and issues an access token."),
    E("POST", "/_security/saml/logout", "Security", "SAML logout",
      "Starts single-logout for a SAML session."),
    E("POST", "/_security/saml/invalidate", "Security", "SAML invalidate",
      "Invalidates a SAML access token after processing a LogoutRequest."),
    E("POST", "/_security/saml/complete_logout", "Security", "SAML complete logout",
      "Acknowledges the IdP's logout completion."),
    E("POST", "/_security/oidc/prepare", "Security", "OpenID prepare authentication",
      "Starts an OpenID Connect login flow."),
    E("POST", "/_security/oidc/authenticate", "Security", "OpenID authenticate",
      "Consumes the OIDC provider's response and issues tokens."),
    E("POST", "/_security/oidc/logout", "Security", "OpenID logout",
      "Ends an OpenID Connect session."),
]
