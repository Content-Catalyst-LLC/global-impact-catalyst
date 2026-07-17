# Global Impact Catalyst

Global Impact Catalyst is an open, reproducible impact-measurement module for Sustainable Catalyst. It turns goals, indicators, reporting periods, sources, methods, and measurements into traceable records that can be reviewed, exported, and reused.

The project is intentionally lightweight. It is not a proprietary ESG platform, certification tool, assurance product, causal-proof engine, or automatic truth system. It is a practical evidence layer for structured impact thinking: define the goal, choose the indicator, document the source, calculate progress, preserve the method, and keep judgment visible.

## v1.0.1 integrity release

v1.0.1 establishes a tested contract between the Python engine, browser engine, schemas, fixtures, examples, and WordPress demo. It fixes boolean coercion, null-versus-zero drift, optional-value handling, calculation-language differences, schema gaps, repeated-shortcode IDs, and insufficient edge-case coverage.

## What this repository includes

- Browser-based WordPress demo using `[global_impact_catalyst_demo]`
- Dependency-light Python impact-record generator
- Versioned input and output JSON Schemas
- Twelve canonical cross-runtime fixtures
- JSON and Markdown export support
- Methodology, quality-rubric, review, export, and repository documentation
- Python, schema, browser-parity, WordPress, and release-contract tests
- GitHub Actions validation
- Manifest and release notes

## WordPress demo

The plugin lives in:

```text
wordpress/global-impact-catalyst-demo/
```

Shortcode:

```text
[global_impact_catalyst_demo]
```

The shortcode supports multiple instances on one page without duplicate HTML IDs. The demo includes accessible validation feedback and exports the same canonical record shape tested by the Python engine.

## Python quick start

```bash
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_record.json \
  --markdown outputs/sample_global_impact_brief.md
```

A fixed timestamp can be supplied for reproducible artifacts:

```bash
python3 python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_record.json \
  --generated-at 2026-07-17T16:00:00+00:00
```

## Development validation

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest
python3 scripts/check_contracts.py
node scripts/check_browser_parity.js
```

The complete portable check is:

```bash
python3 scripts/smoke_test.py
```

## Cross-runtime parity

The Python and browser implementations are independently executable but governed by the same golden fixture suite in `contracts/fixtures/`. Each fixture supplies an input, a fixed generation timestamp, and a complete expected output. CI verifies that both runtimes produce that output exactly.

Canonical behavior includes:

- Recognized boolean parsing rather than generic truthiness
- Missing optional numbers represented as `null`
- Explicit zero values preserved as zero
- Half-away-from-zero output rounding
- Shared enum normalization
- Shared status language and interpretation notes
- Shared traceability path and boundary statements
- Shared quality-score component rubric

## Data completeness and review signal

`metrics.data_quality_score` is a transparent documentation and review heuristic, not an objective evidence-quality rating. Its four components are:

- Source documented: 0 or 25
- Method documented with at least 20 characters: 0 or 25
- Confidence signal: 5, 15, or 25
- Review signal: 0, 10, or 25

The score does not establish truth, reliability, causality, assurance, or certification.

## Repository structure

```text
app/                         Application-facing wrapper
app/tests/                   Wrapper tests
contracts/fixtures/          Cross-runtime golden fixtures
python/                      Canonical Python computation engine
schemas/                     Versioned input and output contracts
data/                        Canonical sample input
examples/                    Validated example output and brief
docs/                        Methodology and release documentation
scripts/                     Fixture, parity, contract, and smoke checks
tests/                       Core, schema, parity, and WordPress tests
wordpress/global-impact-catalyst-demo/  WordPress shortcode plugin
release/                     Version-specific release notes
.github/workflows/           Continuous integration
outputs/                     Generated local outputs; ignored except .gitkeep
```

## Methodological stance

Global Impact Catalyst follows a traceability-first path:

```text
goal → indicator → baseline → current measurement → target → source → method notes → confidence → review status
```

The module makes impact calculations more inspectable. It does not certify SDG alignment, guarantee outcomes, replace professional evaluation, or supply proprietary datasets.

## License

See `LICENSE`. Repository materials are provided for educational, research, and prototyping use. Review applicable legal, privacy, compliance, evaluation, and reporting obligations before formal use.
