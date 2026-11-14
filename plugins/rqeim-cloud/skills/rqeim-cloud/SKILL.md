---
name: rqeim-cloud
description: Work on the applications in a Rqeim Cloud account. Use when a person asks to deploy, preview, diagnose, read logs from, open a domain for, back up, or roll back an app hosted on Rqeim Cloud, or asks what is broken.
---

# Rqeim Cloud

The `rqeim-cloud` MCP server (already connected through this plugin) manages the applications on the
person's Rqeim Cloud account.

## Always start here

Call `read_guide` once in a conversation. It is the current and complete description of the workflow
and of the rules, and the service keeps it up to date — never save a copy of it, never trust a copy
you saved earlier.

## How the account is organised

- **Project**: a Git repository, in the person's Rqeim organisation.
- **Environment**: a copy of a project where work happens. It has its own branch (`env-<name>`), its
  own machines, and its own preview addresses. A long-lived environment is the normal place for
  private data or a different migration; otherwise delete it when the work is done.
- **Production**: follows the default branch. A push to it deploys by itself.
- **Machine**: the isolated VM behind an environment (one for code, one for data when the project
  declares a database).

## The loop

1. **Read.** `list_projects`, `get_project`, `list_environments`. When the person says something is
   broken, start with `get_projects_health` instead of guessing.
2. **Change in a copy.** `create_environment`, then `workspace_shell` (waits for a long command),
   `workspace_view`, `workspace_edit`. Several pieces of work can share one copy, each on its own
   port with `add_preview`.
3. **See it.** Look at the preview, not at production. `read_environment_logs` when it does not come
   up.
4. **Publish or discard.** `finish_task` pushes the commit to the production branch fast-forward and
   deploys, then removes the copy; `delete_environment` discards it. Both need the person's explicit
   permission in the conversation.

## Rules that are easy to get wrong

- A change never happens inside the request: it is queued and returns a task key. Follow it with
  `get_task` (it waits up to 80 seconds). Honour `retryAfterSeconds`. Do not call the same change
  again while its task is queued or running: repeats cancel each other.
- Every write takes a `requestId`; it is generated for you when omitted and returned in the result.
  Reuse the same `requestId` only to retry the same intent.
- Destructive and production tools need `confirm: true`, and only after the person agrees.
- An error with code `uncertain` means the outcome is unknown. Read the current state before
  retrying; never retry blind.
- Never print a token, an API key, or an environment secret in the conversation.

## Times

A redeploy takes 10–40 seconds; a first deploy about a minute; a copy is ready in about 25 seconds.
Allow up to 20 minutes before calling a task stuck.

## Dates and numbers

Every time in a result is ISO 8601 in UTC.
