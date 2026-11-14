# Rqeim Cloud MCP — privacy policy

The canonical, published version of this policy is at `https://rqeim.com/privacy`. Effective from the
date it is published there.

This policy covers the Rqeim Cloud MCP server at `https://cloud.rqeim.com/mcp`, which lets an AI
assistant (for example ChatGPT, Claude, Gemini CLI, Claude Code, Codex) act on a Rqeim Cloud account
on behalf of the person who connected it.

## Who we are

Rqeim Cloud is operated by Rqeim. Contact: support@rqeim.com.

## What we collect

We collect only what the account and the request require:

- **Account identity**: the email address and account identifier of the person who signs in, the
  session, and the OAuth client that connected.
- **What the assistant asks for**: the tool name and its arguments (for example a project name, an
  environment name, a shell command, a file path).
- **What the tools produce**: the account's projects, environments, logs, metrics, deploy history,
  domains and backup metadata, as far as the request needs.
- **Technical records**: request time, response status, and the request identifier we return to the
  assistant. Kept for security and support.

We do not collect: conversation content beyond the tool call, payment card data, government
identifiers, health data, or authentication secrets of other services.

## How we use it

- to carry out the request (create or change an environment, deploy, read logs);
- to authenticate and authorise the account;
- to keep the service secure and working (rate limits, abuse prevention, error diagnosis);
- to bill the account for the resources it uses, from the account's own balance.

We do not use tool calls or their results for advertising, profiling, or training models.

## Who we share it with

- **Providers we run the service on**: the cloud host that runs the account's machines, the object
  storage that holds backups, and the code host that holds the project repositories. They process
  data to provide those services to us.
- **Nothing else.** We do not sell data and do not share it with the AI provider that made the call;
  the assistant's provider receives only what it asks for.

## Where it is stored and for how long

Data lives on servers we operate, in the region shown in the Rqeim Cloud dashboard.

| Data | Retention |
| --- | --- |
| Projects, environments, code | Until the project or environment is deleted, then 30 days for backups |
| Logs and metrics | Metrics 30 days; application logs follow the project's setting (7 days by default) |
| Deploy history | For the life of the project |
| Request records (tool name, status, request id) | 30 days |
| Backups | 7 daily, 4 weekly, and 30 days after deletion |

## Your controls

- Disconnect the connector at any time from the client that connected it; the OAuth token is revoked
  immediately and the account can revoke every connection from its settings page.
- Delete a project, an environment, or the whole account from the dashboard.
- Ask for a copy of the account's data, or its deletion, at support@rqeim.com.

## Security

Traffic is HTTPS only. Tokens are short-lived and scoped to this server alone. Credentials for the
providers we use never reach the assistant or its client.

## Changes

We publish any change to this policy on this page and update the date above. A material change is
announced in the dashboard before it takes effect.
