# Repository Architecture

```text
app/                         Application-facing wrapper
python/                      Core impact record generator
schemas/                     JSON schema
data/                        Sample input
examples/                    Example generated outputs
docs/                        Methodology and governance notes
wordpress/global-impact-catalyst-demo/  WordPress shortcode plugin
tests/                       Python tests
outputs/                     Local generated outputs
```

The core logic is intentionally isolated in `python/global_impact_core.py` so it can be used by scripts, tests, app wrappers, and future UI layers without duplicating calculation logic.
