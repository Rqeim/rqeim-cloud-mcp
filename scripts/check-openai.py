#!/usr/bin/env python3
"""Checks the ChatGPT package against the directory's published limits.

Everything here is a rule from developers.openai.com/plugins (guidelines, submission, and the
submission-errors table). Run it before uploading; it exits non-zero on the first hard failure
and lists warnings separately.

Usage: python3 scripts/check-openai.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "openai")
DIRECTORY_TOOLS_FILE = os.path.join(
    ROOT, "..", "cloud.rqeim.com", "app", "operations", "mcp.ts"
)

CATEGORIES = {
    "Productivity", "Creativity", "Developer Tools", "Business & Operations",
    "Data & Analytics", "Communication", "Education & Research", "Security",
    "Finance", "Healthcare", "Travel", "Entertainment", "Other",
}

failures, warnings = [], []


def fail(msg):
    failures.append(msg)


def warn(msg):
    warnings.append(msg)


def contrast(hex_color, other):
    def lum(h):
        h = h.lstrip("#")
        parts = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in parts]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]

    a, b = lum(hex_color), lum(other)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def directory_tool_names():
    try:
        src = open(DIRECTORY_TOOLS_FILE, encoding="utf-8").read()
    except OSError:
        warn("cloud.rqeim.com not checked out next to this repo: skipped the tool-name cross-check")
        return None
    block = re.search(r"export const DIRECTORY_TOOLS = \[(.*?)\] as const", src, re.S)
    return set(re.findall(r"'([a-z0-9_]+)'", block.group(1))) if block else None


def main():
    plugin = json.load(open(os.path.join(PKG, "plugin.json"), encoding="utf-8"))
    mcp = json.load(open(os.path.join(PKG, "mcp.json"), encoding="utf-8"))
    oai = plugin.get("extensions", {}).get("com.openai", {})
    ui = oai.get("interface", {})

    # --- identity -----------------------------------------------------------
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", plugin.get("name", "")):
        fail("name must start with an ASCII letter or digit, use only letters/digits/_/- and be <= 64 chars")
    if not re.fullmatch(r"\d+\.\d+\.\d+([-+][0-9A-Za-z.-]+)?", plugin.get("version", "")):
        fail("version must be a semantic version")
    for key in ("description", "author", "homepage"):
        if not plugin.get(key):
            fail(f"root {key} is required")

    # --- listing text -------------------------------------------------------
    checks = [
        ("displayName", ui.get("displayName"), 30),
        ("shortDescription", ui.get("shortDescription"), 30),
        ("longDescription", ui.get("longDescription"), 4000),
        ("developerName", ui.get("developerName"), 80),
    ]
    for field, value, limit in checks:
        if not isinstance(value, str) or not value.strip():
            fail(f"interface.{field} is required")
        elif len(value) > limit:
            fail(f"interface.{field} is {len(value)} characters, limit {limit}")
    if ui.get("category") not in CATEGORIES:
        fail(f"interface.category must be one of {sorted(CATEGORIES)}")

    caps = ui.get("capabilities") or []
    if len(caps) > 20:
        fail("interface.capabilities has more than 20 entries")
    if len({c.strip().lower() for c in caps}) != len(caps):
        fail("interface.capabilities has duplicates")
    for cap in caps:
        if not cap.strip() or "\n" in cap or len(cap) > 120:
            fail(f"capability must be one non-empty line of <= 120 chars: {cap!r}")

    prompts = ui.get("defaultPrompt") or []
    if isinstance(prompts, str):
        prompts = [prompts]
    if len(prompts) > 3:
        fail("interface.defaultPrompt accepts at most three prompts")
    if len({p.strip() for p in prompts}) != len(prompts):
        fail("interface.defaultPrompt has duplicates")
    for p in prompts:
        if len(p) > 128 or "\n" in p:
            fail(f"prompt must be one line of <= 128 chars: {p!r}")
        if "@" in p:
            fail(f"prompt must not carry an @mention: {p!r}")

    for field in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        value = ui.get(field)
        if not isinstance(value, str) or not value.startswith("https://"):
            fail(f"interface.{field} must be an HTTPS URL (required for MCP review)")
        elif len(value) > 1024:
            fail(f"interface.{field} is longer than 1024 characters")

    for field in ("brandColor", "brandColorDark"):
        value = ui.get(field)
        if value is None:
            continue
        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
            fail(f"interface.{field} must be #RRGGBB")
            continue
        against = "#FFFFFF" if field == "brandColor" else "#212121"
        if contrast(value, against) < 2:
            fail(f"interface.{field} {value} has less than 2:1 contrast against {against}")

    # --- icons --------------------------------------------------------------
    for field, limit in (("composerIcon", "Codex"), ("logo", "the listing")):
        rel = ui.get(field)
        if not rel:
            fail(f"interface.{field} is required for {limit}")
            continue
        if not rel.startswith("./"):
            fail(f"interface.{field} must be a ./ path relative to the plugin root")
        path = os.path.join(PKG, rel)
        if not os.path.isfile(path):
            fail(f"{rel} is referenced but missing")
            continue
        if os.path.getsize(path) > 5 * 1024 * 1024:
            fail(f"{rel} is larger than 5 MiB")
        # PNG header: width and height live at bytes 16..24.
        with open(path, "rb") as fh:
            head = fh.read(24)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            width = int.from_bytes(head[16:20], "big")
            height = int.from_bytes(head[20:24], "big")
            if width != height or width < 48 or width > 4096:
                fail(f"{rel} is {width}x{height}; must be square, 48..4096")
        else:
            warn(f"{rel} is not a PNG; check it by hand (square, >= 48px, <= 5 MiB)")

    # --- MCP declaration ----------------------------------------------------
    servers = mcp.get("mcpServers", {})
    if len(servers) != 1:
        fail("exactly one MCP server may be declared")
    for name, server in servers.items():
        if server.get("type") != "streamable-http":
            fail(f"{name}: type must be streamable-http")
        url = server.get("url", "")
        if not url.startswith("https://"):
            fail(f"{name}: url must be HTTPS")
        if "?" in url:
            warn(f"{name}: url carries a query string; a portal may drop it")
    if "apps" in plugin.get("extensions", {}).get("com.openai", {}) or os.path.exists(
        os.path.join(PKG, ".app.json")
    ):
        fail("the ZIP must not reference apps / .app.json")

    # --- review material ----------------------------------------------------
    review = oai.get("review", {})
    cases = review.get("test_cases", {})
    positive, negative = cases.get("positive", []), cases.get("negative", [])
    if len(positive) != 5:
        fail(f"exactly five positive test cases are required, found {len(positive)}")
    if len(negative) != 3:
        fail(f"exactly three negative test cases are required, found {len(negative)}")
    known = directory_tool_names()
    for index, case in enumerate(positive, 1):
        for field in ("description", "prompt", "tools_triggered", "expected_behavior"):
            if not case.get(field):
                fail(f"positive case {index}: {field} is required")
        if known is not None:
            for tool in [t.strip() for t in case.get("tools_triggered", "").split(",") if t.strip()]:
                if tool not in known:
                    fail(f"positive case {index}: {tool} is not on the directory surface")
    for index, case in enumerate(negative, 1):
        for field in ("description", "prompt"):
            if not case.get(field):
                fail(f"negative case {index}: {field} is required")
    if not review.get("demo_recording_url"):
        warn("review.demo_recording_url is missing; MCP review requires a walkthrough video")

    # --- publication --------------------------------------------------------
    publication = oai.get("publication", {})
    for code in publication.get("countries", []):
        if not re.fullmatch(r"[A-Z]{2}", code):
            fail(f"country code {code!r} must be uppercase ISO-3166 alpha-2")
    for locale, text in (publication.get("translations") or {}).items():
        if not re.fullmatch(r"[a-z]{2}(-[A-Z]{2})?", locale):
            fail(f"translation key {locale!r} must look like ar or pt-BR")
        if len(text.get("subtitle", "")) > 30:
            fail(f"translation {locale}: subtitle is longer than 30 characters")
        if len(text.get("description", "")) > 4000:
            fail(f"translation {locale}: description is longer than 4000 characters")

    # --- report -------------------------------------------------------------
    for line in warnings:
        print(f"  warn  {line}")
    for line in failures:
        print(f"  FAIL  {line}")
    print(f"\n{len(failures)} failures, {len(warnings)} warnings")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
