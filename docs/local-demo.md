# Local Demo

```bash
python3 -m pip install -r requirements-dev.txt
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_contract.json \
  --markdown outputs/sample_global_impact_brief.md
python3 -m pytest -q
node scripts/check_browser_parity.js
```
