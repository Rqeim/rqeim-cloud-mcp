# n8n

Two ways to use Rqeim Cloud from n8n.

## 1. Health digest (works today, no MCP)

`rqeim-cloud-health-digest.json` — import it in n8n (**Workflows → Import from File**), then set:

| Where | What |
| --- | --- |
| The **Header Auth** credential on *Rqeim Cloud health* | Name `Authorization`, Value `Bearer <token>` — create the token in Rqeim Cloud → Settings → API |
| Environment variable `RQEIM_ALERT_WEBHOOK` | Any endpoint that accepts `{ "text": "…" }` (Slack, Discord, Google Chat, your own server) |

It asks `GET https://cloud.rqeim.com/api/v1/health` every six hours and tells you only when something
is broken: a failed deploy, an address that stopped answering, a nearly full disk, a late backup.

## 2. The MCP path on n8n

n8n's **MCP Client Tool** node speaks the *SSE* transport and expects an `SSE Endpoint`. Rqeim Cloud
serves Streamable HTTP at `https://cloud.rqeim.com/mcp` and does not expose an SSE endpoint, so that
node cannot reach it today. Two ways forward:

- use the REST API (the workflow above) — every tool in the MCP server has a REST twin under
  `https://cloud.rqeim.com/api/v1`;
- or ask us for the SSE door; it needs session affinity in front of the two replicas, so it is a
  decision, not a switch.

## One-click install elsewhere

[![Add to Kiro](https://kiro.dev/images/add-to-kiro.svg)](https://kiro.dev/launch/mcp/add?name=Rqeim%20Cloud&config=%7B%22url%22%3A%22https%3A//cloud.rqeim.com/mcp%22%2C%22disabled%22%3Afalse%2C%22autoApprove%22%3A%5B%5D%7D)

The same install link works for anyone: it hands Kiro the address `https://cloud.rqeim.com/mcp` and
lets Kiro run the OAuth sign-in.
