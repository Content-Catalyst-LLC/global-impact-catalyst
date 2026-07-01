(function () {
  const example = {
    initiative: 'Community Energy Retrofit Pilot',
    goal: 'Reduce household energy burden while improving residential efficiency.',
    sdgTheme: 'Affordable and clean energy',
    indicator: 'Average monthly bill reduction',
    unit: 'USD',
    higherIsBetter: 'true',
    baselinePeriod: '2025 baseline',
    currentPeriod: '2026 Q2',
    baseline: 0,
    current: 18,
    target: 30,
    beneficiaries: 420,
    budget: 125000,
    confidence: 'medium',
    reviewStatus: 'needs_review',
    source: 'Pilot utility-billing sample and participant survey summary',
    method: 'Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.'
  };

  function n(value, fallback) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  function pct(numerator, denominator) {
    if (denominator === 0) return null;
    return (numerator / denominator) * 100;
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function collect(form) {
    const data = new FormData(form);
    return {
      record_type: 'global_impact_catalyst_record',
      generated_at: new Date().toISOString(),
      initiative: String(data.get('initiative') || '').trim(),
      goal: String(data.get('goal') || '').trim(),
      sdg_theme: String(data.get('sdgTheme') || '').trim(),
      indicator: String(data.get('indicator') || '').trim(),
      unit: String(data.get('unit') || '').trim(),
      higher_is_better: data.get('higherIsBetter') === 'true',
      baseline_period: String(data.get('baselinePeriod') || '').trim(),
      current_period: String(data.get('currentPeriod') || '').trim(),
      baseline_value: n(data.get('baseline'), 0),
      current_value: n(data.get('current'), 0),
      target_value: n(data.get('target'), 0),
      beneficiaries: Math.max(0, Math.round(n(data.get('beneficiaries'), 0))),
      budget_usd: Math.max(0, n(data.get('budget'), 0)),
      confidence: String(data.get('confidence') || 'medium'),
      review_status: String(data.get('reviewStatus') || 'draft'),
      source: String(data.get('source') || '').trim(),
      method_notes: String(data.get('method') || '').trim()
    };
  }

  function quality(record) {
    let score = 0;
    if (record.source) score += 25;
    if (record.method_notes.length >= 20) score += 25;
    if (record.confidence === 'high') score += 25;
    else if (record.confidence === 'medium') score += 15;
    else score += 5;
    if (record.review_status === 'reviewed' || record.review_status === 'published') score += 25;
    else if (record.review_status === 'needs_review') score += 10;
    return Math.min(100, score);
  }

  function progress(record) {
    if (record.higher_is_better) {
      return pct(record.current_value - record.baseline_value, record.target_value - record.baseline_value);
    }
    return pct(record.baseline_value - record.current_value, record.baseline_value - record.target_value);
  }

  function status(progressValue, record) {
    const prefix = record.review_status === 'draft' || record.review_status === 'needs_review' ? 'draft — ' : 'reviewed — ';
    if (progressValue === null || !Number.isFinite(progressValue)) return 'needs baseline/target review';
    if (record.confidence === 'low') return prefix + 'interpret cautiously';
    if (progressValue >= 100) return prefix + 'target reached or exceeded';
    if (progressValue >= 75) return prefix + 'near target';
    if (progressValue >= 40) return prefix + 'partial progress';
    if (progressValue >= 0) return prefix + 'early progress';
    return prefix + 'moving away from target';
  }

  function enrich(record) {
    const absoluteChange = record.current_value - record.baseline_value;
    const percentChange = pct(absoluteChange, record.baseline_value);
    const progressValue = progress(record);
    const remainingGap = record.higher_is_better ? record.target_value - record.current_value : record.current_value - record.target_value;
    const costPerBeneficiary = record.beneficiaries > 0 ? record.budget_usd / record.beneficiaries : null;
    record.metrics = {
      absolute_change: Number(absoluteChange.toFixed(4)),
      percent_change_from_baseline: percentChange === null ? null : Number(percentChange.toFixed(2)),
      progress_to_target_percent: progressValue === null || !Number.isFinite(progressValue) ? null : Number(progressValue.toFixed(2)),
      remaining_gap: Number(remainingGap.toFixed(4)),
      cost_per_beneficiary_usd: costPerBeneficiary === null ? null : Number(costPerBeneficiary.toFixed(2)),
      data_quality_score: quality(record),
      status: status(progressValue, record)
    };
    record.interpretation_notes = [
      `${record.indicator} changed from ${record.baseline_value} ${record.unit} in ${record.baseline_period} to ${record.current_value} ${record.unit} in ${record.current_period}.`,
      'Progress should be interpreted against the indicator definition, data source, method notes, confidence level, and review status.',
      record.metrics.progress_to_target_percent === null ? 'Progress to target could not be calculated because the baseline and target need review.' : `Estimated progress to target is ${record.metrics.progress_to_target_percent}%.`
    ];
    record.traceability_path = ['goal', 'indicator', 'baseline', 'current measurement', 'target', 'source', 'method notes', 'confidence', 'review status'];
    record.boundaries = [
      'This record is not ESG assurance or SDG certification.',
      'Results depend on source quality, indicator definition, data comparability, and method choices.',
      'Human review is required before formal reporting or external claims.'
    ];
    return record;
  }

  function render(root, record) {
    const progressEl = root.querySelector('[data-gic-progress]');
    const qualityEl = root.querySelector('[data-gic-quality]');
    const statusEl = root.querySelector('[data-gic-status]');
    const bar = root.querySelector('[data-gic-bar]');
    const result = root.querySelector('[data-gic-result]');
    const jsonEl = root.querySelector('[data-gic-json]');
    const progressValue = record.metrics.progress_to_target_percent;

    progressEl.textContent = progressValue === null ? 'n/a' : `${progressValue}%`;
    qualityEl.textContent = `${record.metrics.data_quality_score}/100`;
    statusEl.textContent = record.metrics.status;
    bar.style.width = `${clamp(progressValue || 0, 0, 100)}%`;

    result.innerHTML = `
      <h3>${escapeHtml(record.initiative || 'Untitled initiative')}</h3>
      <p><strong>Goal:</strong> ${escapeHtml(record.goal || 'No goal entered')}</p>
      <p><strong>Indicator:</strong> ${escapeHtml(record.indicator)} (${escapeHtml(record.unit)})</p>
      <p><strong>Theme:</strong> ${escapeHtml(record.sdg_theme)}</p>
      <ul>
        <li>Baseline: ${record.baseline_value} ${escapeHtml(record.unit)} (${escapeHtml(record.baseline_period)})</li>
        <li>Current: ${record.current_value} ${escapeHtml(record.unit)} (${escapeHtml(record.current_period)})</li>
        <li>Target: ${record.target_value} ${escapeHtml(record.unit)}</li>
        <li>Remaining gap: ${record.metrics.remaining_gap} ${escapeHtml(record.unit)}</li>
        <li>Cost per beneficiary: ${record.metrics.cost_per_beneficiary_usd === null ? 'n/a' : '$' + record.metrics.cost_per_beneficiary_usd}</li>
      </ul>
      <p><strong>Source:</strong> ${escapeHtml(record.source || 'No source entered')}</p>
      <p><strong>Review:</strong> ${escapeHtml(record.review_status.replace('_', ' '))}; confidence ${escapeHtml(record.confidence)}.</p>
    `;

    jsonEl.textContent = JSON.stringify(record, null, 2);
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' })[char];
    });
  }

  function setExample(form) {
    Object.keys(example).forEach(function (key) {
      const field = form.elements[key];
      if (field) field.value = example[key];
    });
  }

  function download(record) {
    const blob = new Blob([JSON.stringify(record, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'global-impact-catalyst-record.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-gic-demo]').forEach(function (root) {
      const form = root.querySelector('[data-gic-form]');
      let currentRecord = enrich(collect(form));
      render(root, currentRecord);

      form.addEventListener('submit', function (event) {
        event.preventDefault();
        currentRecord = enrich(collect(form));
        render(root, currentRecord);
      });

      root.querySelector('[data-gic-reset]').addEventListener('click', function () {
        setExample(form);
        currentRecord = enrich(collect(form));
        render(root, currentRecord);
      });

      root.querySelector('[data-gic-download]').addEventListener('click', function () {
        currentRecord = enrich(collect(form));
        render(root, currentRecord);
        download(currentRecord);
      });
    });
  });
}());
