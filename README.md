# Global Impact Catalyst

Global Impact Catalyst is an open, reproducible impact-measurement module for Sustainable Catalyst. It helps turn goals, indicators, reporting periods, sources, methods, and measurements into traceable records that can be reviewed, exported, and reused.

The project is intentionally lightweight. It is not a proprietary ESG platform, certification tool, or automatic truth system. It is a practical evidence layer for structured impact thinking: define the goal, choose the indicator, document the source, calculate progress, preserve the method, and keep judgment visible.

## What this repository includes

- A browser-based WordPress demo plugin using the shortcode `[global_impact_catalyst_demo]`
- A dependency-light Python impact-record generator
- JSON schema for impact records
- Sample inputs and example exports
- Methodology, review, and export documentation
- Tests and GitHub Actions validation
- A manifest describing repository structure and demo scope

## Demo

The WordPress plugin lives in:

```text
wordpress/global-impact-catalyst-demo/
```

Shortcode:

```text
[global_impact_catalyst_demo]
```

The demo lets visitors build a traceable impact record with:

- Initiative or program name
- Goal / outcome statement
- SDG-style theme
- Indicator and unit
- Baseline, current, and target values
- Reporting period
- Source and method notes
- Confidence level and review status
- Beneficiary count and optional budget
- JSON export

## Python quick start

```bash
python python/global_impact_core.py \
  --input data/sample_global_impact_input.json \
  --output outputs/sample_global_impact_record.json \
  --markdown outputs/sample_global_impact_brief.md
```

Run tests:

```bash
python -m pytest
```

## Repository structure

```text
app/                         Optional app-facing wrapper
app/tests/                   App wrapper tests
python/                      Core impact computation logic
schemas/                     JSON schemas
data/                        Sample input data
examples/                    Example output records and briefs
docs/                        Methodology and review documentation
wordpress/global-impact-catalyst-demo/  WordPress shortcode plugin
tests/                       Core Python tests
.github/workflows/           CI validation
outputs/                     Generated local outputs; ignored except .gitkeep
```

## Methodological stance

Global Impact Catalyst follows a traceability-first approach:

```text
goal → indicator → definition → source → baseline → measurement → method → interpretation → review
```

The module is designed to make impact claims more inspectable. It does not certify SDG alignment, guarantee outcomes, replace professional evaluation, or supply proprietary datasets.

## License

See `LICENSE` if present in the repository. Repository materials are provided for educational, research, and prototyping use. Review legal, compliance, and reporting obligations before using outputs in formal contexts.
