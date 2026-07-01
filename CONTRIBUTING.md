# Contributing

Global Impact Catalyst is designed as a small, inspectable, evidence-oriented module. Contributions should preserve that character.

## Preferred contribution types

- Clearer methodology notes
- Better sample records
- More robust validation checks
- Safer export formats
- Documentation improvements
- Tests for edge cases
- Accessibility improvements for the WordPress demo

## Standards

Contributions should keep claims traceable. New examples should include source notes, method notes, assumptions, and interpretation limits. Avoid language that implies automatic certification, legal compliance, ESG assurance, or guaranteed impact.

## Local validation

```bash
python -m pytest
python python/global_impact_core.py --input data/sample_global_impact_input.json --output outputs/sample_global_impact_record.json --markdown outputs/sample_global_impact_brief.md
```

## Style

- Prefer plain language over jargon.
- Keep calculations transparent.
- Keep examples educational and reviewable.
- Do not add unnecessary dependencies.
