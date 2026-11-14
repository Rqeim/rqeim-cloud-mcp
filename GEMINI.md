# Rqeim Cloud

The `rqeim-cloud` MCP server manages the applications on the person's Rqeim Cloud account. The
server signs in through the browser the first time it is used.

## Before you change anything

Call `read_guide` once in a conversation. It is the current and complete description of the workflow
and its rules, and it is updated by the service — never save a copy of it.

## What the account is

A **project** is a Git repository. An **environment** is a copy of a project where work happens, with
its own preview addresses and its own branch. **Production** follows the default branch: a push to it
deploys by itself.

## How work is done

1. Read what exists first: `list_projects`, `get_project`, `list_environments`, and
   `get_projects_health` when the person reports something broken.
2. Change code in a copy, never on production: `create_environment`, then `workspace_shell`,
   `workspace_view`, `workspace_edit`, and a preview per piece of work with `add_preview`.
3. Publish with `finish_task` (it pushes and deploys) or discard with `delete_environment`. Both need
   the person's explicit permission in the conversation.

## Rules

- Reads change nothing and need no confirmation. A tool that changes something takes a `requestId`
  (generated for you when omitted and returned in the result; reuse it to retry the same intent, not
  to repeat a change you already made).
- A change never happens in the request: it is queued and returns a task key. Follow it with
  `get_task`, which waits up to 80 seconds; honour the `retryAfterSeconds` it returns.
- Destructive and production tools need `confirm: true`, and only after the person agrees.
- An error with code `uncertain` means the outcome is unknown: read the current state before
  retrying.
- Never print a token, a key, or an environment secret in the conversation.

## Dates and numbers

Every time in a result is ISO 8601 in UTC.
