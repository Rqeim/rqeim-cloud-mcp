#!/bin/sh
# Rqeim Cloud: do not end the turn while the last Rqeim answer still lists unfinished work.
# Every Rqeim answer about a project carries "pending": [] when nothing is left, or the steps
# that are. This reads the newest one in the transcript; a non-empty list asks the agent to
# go on once. A second stop in a row is let through, so the agent can always end the turn by
# telling the user what is left. Reads only; needs nothing but sh, sed, grep and tail.
input=$(cat)
case "$input" in *'"stop_hook_active":true'*) exit 0 ;; esac
transcript=$(printf '%s' "$input" | sed -n 's/.*"transcript_path"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
[ -n "$transcript" ] && [ -f "$transcript" ] || exit 0
last=$(tail -n 500 "$transcript" | grep -o '\\"pending\\":\[[^]]*\]' | tail -n 1)
case "$last" in '' | '\"pending\":[]') exit 0 ;; esac
left=$(printf '%s' "$last" | sed 's/^\\"pending\\":\[//; s/\]$//; s/\\"//g; s/"/'"'"'/g')
printf '{"decision":"block","reason":"Rqeim still lists unfinished work. %s Finish it (follow the task or deploy to its end, rate the deploy), then stop. If it cannot be finished now, tell the user exactly what is left and why."}\n' "$left"
