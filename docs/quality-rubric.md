# Data Completeness and Review Rubric

Global Impact Catalyst v1.0.1 reports a 0–100 documentation and review signal. The value is deliberately simple and fully decomposed in `metrics.data_quality_components`.

| Component | Rule | Points |
|---|---|---:|
| Source documented | Nonblank source field | 25 |
| Method documented | Trimmed method note has at least 20 characters | 25 |
| Confidence signal | Low / medium / high | 5 / 15 / 25 |
| Review signal | Draft / needs review / reviewed or published | 0 / 10 / 25 |

The total is the sum of these four components, capped at 100.

## Interpretation boundary

This signal measures the presence of documentation and selected review metadata. It does not inspect whether a source is accurate, whether a method is appropriate, whether observations are representative, whether attribution is causal, or whether a claim is true. It must not be presented as assurance, certification, audit scoring, or an objective evidence-quality grade.
