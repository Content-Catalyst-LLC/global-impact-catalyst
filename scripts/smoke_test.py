#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    run(sys.executable, "-m", "pytest", "-q")
    run(sys.executable, "scripts/check_contracts.py")
    run("php", "scripts/check_wordpress_instances.php")
    with tempfile.TemporaryDirectory(prefix="gic-v101-") as directory:
        output = Path(directory) / "record.json"
        brief = Path(directory) / "brief.md"
        run(
            sys.executable,
            "python/global_impact_core.py",
            "--input",
            "data/sample_global_impact_input.json",
            "--output",
            str(output),
            "--markdown",
            str(brief),
            "--generated-at",
            "2026-07-17T16:00:00+00:00",
        )
        data = json.loads(output.read_text())
        assert data["record_type"] == "global_impact_catalyst_record"
        assert data["metrics"]["progress_to_target_percent"] == 60.0
        assert brief.read_text().startswith("# Global Impact Catalyst Brief")
    print("Portable release smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
