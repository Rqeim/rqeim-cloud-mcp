# Installing Rqeim Cloud (for an agent)

Rqeim Cloud is a **remote** MCP server. There is nothing to clone, build or run locally, and no
API key to paste: it is a Streamable HTTP endpoint with standard MCP authorization (OAuth 2.1).

```json
{
  "mcpServers": {
    "rqeim-cloud": {
      "type": "streamable-http",
      "url": "https://cloud.rqeim.com/mcp"
    }
  }
}
```

Claude Code:

```bash
claude mcp add --transport http rqeim-cloud https://cloud.rqeim.com/mcp
```

## What happens on first use

1. The server answers `401` with `WWW-Authenticate` pointing at
   `https://cloud.rqeim.com/.well-known/oauth-protected-resource/mcp`.
2. Register a client dynamically (RFC 7591) at the registration endpoint named in
   `https://cloud.rqeim.com/.well-known/oauth-authorization-server`.
3. Run the authorization code flow with PKCE (S256). The browser opens the Rqeim sign-in page; the
   user signs in and presses **Allow**. A `localhost` redirect URI is fine.
4. Send `Authorization: Bearer <access_token>` on every request. The token lasts one hour; refresh
   it with the refresh token (60 days).

## If OAuth is not supported by the client

Ask the user for an API token from `https://cloud.rqeim.com/dashboard/settings` (the API section)
and send it as the same `Authorization: Bearer <token>` header. Tokens are created and revoked
there; there is no other key.

## What the tools do

Sixteen named tools cover: reading projects, health, deploy history and logs; creating a copy of an
application, editing files in it, running commands in it and publishing a preview link; taking a
backup; publishing a copy to production. Tools that change something or touch production require the
user's explicit confirmation (`confirm: true`) and are recorded in the project's deploy log.

Read-only: `read_guide`, `list_projects`, `get_project`, `get_projects_health`, `list_environments`,
`list_deploys`, `read_environment_logs`, `get_task`.
Changing: `create_environment`, `workspace_shell`, `workspace_view`, `workspace_edit`, `add_preview`,
`backup_project`.
Destructive: `finish_task` (publishes to production), `delete_environment`.

A flat directory endpoint (`https://cloud.rqeim.com/mcp/directory`) lists the same sixteen tools
without the discovery layer, for clients and directories that review every tool.
