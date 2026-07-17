# Repository Architecture — v1.0.1

Global Impact Catalyst keeps the runtime small while enforcing observable parity between Python and browser calculations.

```text
input JSON
   ├── Python normalization and engine
   └── JavaScript normalization and engine
            ↓
canonical golden fixtures
            ↓
versioned output schema
            ↓
JSON / Markdown / WordPress presentation
```

The two runtime implementations are tested against complete expected outputs. This avoids requiring Python inside WordPress while preventing ungoverned contract drift.

Release integrity is checked by `scripts/check_contracts.py`; browser parity is checked by `scripts/check_browser_parity.js`; the portable suite is `scripts/smoke_test.py`.
