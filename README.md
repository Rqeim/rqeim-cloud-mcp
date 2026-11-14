# Rqeim Cloud MCP

[![Add to Kiro](https://kiro.dev/images/add-to-kiro.svg)](https://kiro.dev/launch/mcp/add?name=Rqeim%20Cloud&config=%7B%22url%22%3A%22https%3A//cloud.rqeim.com/mcp%22%2C%22disabled%22%3Afalse%2C%22autoApprove%22%3A%5B%5D%7D)


Connect an AI agent to [Rqeim Cloud](https://cloud.rqeim.com) and it can create, deploy, inspect and
diagnose the applications on your account: environments, previews, logs, domains, health and backups.

This repository is the public distribution bundle for the Rqeim Cloud MCP server. It contains no
server code: the server is hosted at `https://cloud.rqeim.com/mcp`.

---

## 1. What the server does

Rqeim Cloud runs Docker applications from a Git repository: you push, it deploys. With this server
an agent works the same way a person does in the dashboard:

- read the account's projects, environments, health and deploy history;
- open a copy of a project, change its code in a sandboxed machine, preview it, and publish it;
- read logs, run scheduled jobs, restore a backup (with explicit confirmation).

Every change is asked for explicitly by the person in the conversation. The server never decides on
its own to deploy, delete, or touch production.

## 2. Connect

### Claude Code

```bash
claude mcp add --transport http rqeim-cloud https://cloud.rqeim.com/mcp
```

Or install the plugin, which also adds the workflow skill:

```bash
claude plugin marketplace add Rqeim/rqeim-cloud-mcp
claude plugin install rqeim-cloud@rqeim
```

Claude Code opens a browser to sign in to your Rqeim account the first time.

### Gemini CLI

```bash
gemini extensions install https://github.com/Rqeim/rqeim-cloud-mcp
```

### ChatGPT and Claude (web, desktop, mobile)

Add a connector with the URL `https://cloud.rqeim.com/mcp/directory` and sign in when asked.
`/mcp/directory` lists every tool by name, which is what a public directory reviews; the plain `/mcp`
keeps the short list and its search for agents. Each door has its own OAuth `resource`.

### Codex and other MCP clients

Streamable HTTP at `https://cloud.rqeim.com/mcp`, OAuth 2.1 with dynamic client registration and
PKCE. An account API token works too, as `Authorization: Bearer <token>`.

## 3. Authentication

The server signs users in with OAuth 2.1, discovered from the standard well-known documents:

| Document | URL |
| --- | --- |
| Protected resource metadata (RFC 9728) | `https://cloud.rqeim.com/.well-known/oauth-protected-resource/mcp` |
| Authorization server metadata (RFC 8414) | `https://cloud.rqeim.com/.well-known/oauth-authorization-server` |

Clients register themselves (`/oauth/register`), use PKCE with `S256`, and receive a token scoped to
`mcp` alone. A token is an hour long, refreshed without a new sign-in.

An unauthenticated request answers:

```http
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer realm="rqeim-cloud", resource_metadata="https://cloud.rqeim.com/.well-known/oauth-protected-resource/mcp", scope="mcp"
```

## 4. Tools

Every tool is one intent. Reads change nothing and answer without confirmation; tools that change
something take a `requestId` (generated when omitted) and destructive or production tools also need
`confirm: true` after the person agrees. A change runs in the background and returns a task key:
follow it with `get_task`.

Naming: `list_projects`, `get_project`, `get_projects_health`, `create_environment`, `workspace_shell`,
`read_environment_logs`, `finish_task`, `delete_environment`, `get_task`, `read_guide`.

Run `read_guide` once per conversation: it is the current, complete description of the workflow and
the rules (written for the model, kept up to date by the service).

## 5. Data and privacy

The server reads and writes only the account that signed in. It stores no conversation content and
returns no telemetry identifiers in tool results. See [PRIVACY.md](PRIVACY.md).

## 6. Limits

- One project belongs to one account; there are no shared workspaces.
- Machine operations (deploy, build, restore) are asynchronous: a redeploy is 10–40 seconds, a first
  deploy about a minute.
- Production is read-and-diagnose for agents: a change goes through an environment first, then a
  deploy.

## 7. Support

- Support: support@rqeim.com
- Documentation: https://rqeim.com/docs/mcp
- Status: https://cloud.rqeim.com/up
- Issues with this bundle: https://github.com/Rqeim/rqeim-cloud-mcp/issues
