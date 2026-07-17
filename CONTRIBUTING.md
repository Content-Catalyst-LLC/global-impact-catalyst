# Contributing

Use Python 3.10+, Node 18+, and PHP 8+ when available.

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
php scripts/check_wordpress_instances.php
python3 scripts/smoke_test.py
```

When contract behavior changes, update both runtimes, regenerate fixtures with `python3 scripts/generate_fixtures.py`, update all schemas and documentation, and add a migration rule when existing records would otherwise lose meaning.

Generated output:

```bash
python3 python/global_impact_core.py --input data/sample_global_impact_input.json --output outputs/sample_global_impact_contract.json --markdown outputs/sample_global_impact_brief.md
```
