#!/usr/bin/env bash
# Builds the ZIP uploaded to the ChatGPT plugin directory.
#
# What goes in: the portable manifest, the MCP declaration (the server URL only — the connection
# itself is completed in the portal), the skills, and the icons. What must not: an `apps` /
# `.app.json` reference, lifecycle hooks, or any credential (the portal rejects all three).
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/dist"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

cp "$root/openai/plugin.json" "$stage/plugin.json"
cp "$root/openai/mcp.json" "$stage/mcp.json"
cp -R "$root/openai/assets" "$stage/assets"
rm -f "$stage/assets/README.md"
mkdir -p "$stage/skills"
cp -R "$root/plugins/rqeim-cloud/skills/." "$stage/skills/"

for asset in icon.png logo.png; do
  [ -f "$stage/assets/$asset" ] || { echo "missing openai/assets/$asset" >&2; exit 1; }
done

mkdir -p "$out"
version="$(node -e "process.stdout.write(require('$root/openai/plugin.json').version)")"
zip_path="$out/rqeim-cloud-plugin-$version.zip"
rm -f "$zip_path"
# -X: no extra attributes, so the archive holds nothing but the files above.
(cd "$stage" && zip -qrX "$zip_path" .)

echo "$zip_path"
