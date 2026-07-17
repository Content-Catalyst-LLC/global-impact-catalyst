#!/usr/bin/env python3
"""Release contract checks for Global Impact Catalyst v1.0.1."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "1.0.1"
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


manifest = json.loads((ROOT / "global_impact_catalyst_manifest.json").read_text())
require(manifest.get("version") == EXPECTED, "manifest version mismatch")
require(manifest.get("shortcode") == "[global_impact_catalyst_demo]", "manifest shortcode mismatch")
for key in ("core_path", "browser_core_path", "plugin_path", "input_schema_path", "schema_path", "fixtures_path"):
    require((ROOT / manifest[key]).exists(), f"manifest path missing: {key} -> {manifest[key]}")

plugin = (ROOT / "wordpress/global-impact-catalyst-demo/global-impact-catalyst-demo.php").read_text()
header = re.search(r"^ \* Version:\s*([^\s]+)", plugin, re.MULTILINE)
constant = re.search(r"define\('GIC_DEMO_VERSION',\s*'([^']+)'\)", plugin)
require(bool(header) and header.group(1) == EXPECTED, "WordPress plugin header version mismatch")
require(bool(constant) and constant.group(1) == EXPECTED, "WordPress plugin constant version mismatch")
require("add_shortcode('global_impact_catalyst_demo'" in plugin, "WordPress shortcode registration missing")
require("static $instance = 0" in plugin and "$id_prefix" in plugin, "per-instance shortcode IDs missing")

for schema_name in ("global_impact_input.schema.json", "global_impact_record.schema.json"):
    schema = json.loads((ROOT / "schemas" / schema_name).read_text())
    require(schema.get("x-global-impact-catalyst-version") == EXPECTED, f"schema version mismatch: {schema_name}")
    require(f"/{EXPECTED}/" in schema.get("$id", ""), f"schema ID is not versioned: {schema_name}")

changelog = (ROOT / "CHANGELOG.md").read_text()
require("## [1.0.1]" in changelog, "CHANGELOG missing v1.0.1")
release_notes = ROOT / "release/v1.0.1.md"
require(release_notes.exists(), "release notes missing")

fixture_files = sorted((ROOT / "contracts/fixtures").glob("*.json"))
require(len(fixture_files) >= 10, "canonical fixture suite must contain at least 10 fixtures")

readme = (ROOT / "README.md").read_text()
require("tests/" in readme, "README repository tree omits tests directory")
require("Cross-runtime parity" in readme, "README parity section missing")

if errors:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    raise SystemExit(1)
print("Global Impact Catalyst v1.0.1 release contract passed.")
