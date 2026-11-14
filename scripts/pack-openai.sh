#!/usr/bin/env bash
# Builds the ZIP uploaded to the ChatGPT plugin directory.
# The directory does not take MCP configuration inside the ZIP (the server is connected through the
# portal), so the package is: manifest + skills + assets.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
out="$root/dist"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

cp "$root/openai/plugin.json" "$stage/plugin.json"
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
(cd "$stage" && zip -qr "$zip_path" .)

echo "$zip_path"
