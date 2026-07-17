(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = api;
  }
  if (root) {
    root.GlobalImpactCatalystCore = api;
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const TRACEABILITY_PATH = ['goal', 'indicator', 'baseline', 'current measurement', 'target', 'source', 'method notes', 'confidence', 'review status'];
  const BOUNDARIES = [
    'This record is not an ESG assurance opinion or SDG certification.',
    'Results depend on data quality, source reliability, indicator definition, and method choices.',
    'Human review is required before formal reporting or external claims.'
  ];
  const example = {
    initiative: 'Community Energy Retrofit Pilot',
    goal: 'Reduce household energy burden while improving residential efficiency.',
    sdg_theme: 'Affordable and clean energy',
    indicator: 'Average monthly bill reduction',
    unit: 'USD',
    higher_is_better: true,
    baseline_period: '2025 baseline',
    current_period: '2026 Q2',
    baseline_value: 0,
    current_value: 18,
    target_value: 30,
    beneficiaries: 420,
    budget_usd: 125000,
    confidence: 'medium',
    review_status: 'needs_review',
    source: 'Pilot utility-billing sample and participant survey summary',
    method_notes: 'Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.'
  };

  function validationError(message) {
    const error = new Error(message);
    error.name = 'InputValidationError';
    return error;
  }

  function text(value, fallback) {
    return String(value === null || typeof value === 'undefined' ? fallback : value).trim();
  }

  function number(value, field, fallback) {
    if (value === null || typeof value === 'undefined' || (typeof value === 'string' && value.trim() === '')) {
      if (typeof fallback !== 'undefined') return Number(fallback);
      throw validationError(`${field} is required`);
    }
    if (typeof value === 'boolean') throw validationError(`${field} must be a finite number`);
    const parsed = Number(value);
    if (!Number.isFinite(parsed)) throw validationError(`${field} must be a finite number`);
    return parsed;
  }

  function optionalNumber(value, field, minimum) {
    if (value === null || typeof value === 'undefined' || (typeof value === 'string' && value.trim() === '')) return null;
    const parsed = number(value, field);
    if (parsed < minimum) throw validationError(`${field} must be greater than or equal to ${minimum}`);
    return parsed;
  }

  function optionalInteger(value, field, minimum) {
    const parsed = optionalNumber(value, field, minimum);
    if (parsed === null) return null;
    if (!Number.isInteger(parsed)) throw validationError(`${field} must be an integer`);
    return parsed;
  }

  function booleanValue(value, field, fallback) {
    if (value === null || typeof value === 'undefined' || value === '') return fallback;
    if (typeof value === 'boolean') return value;
    if (value === 1 || value === '1') return true;
    if (value === 0 || value === '0') return false;
    if (typeof value === 'string') {
      const cleaned = value.trim().toLowerCase();
      if (['true', 'yes', 'y', 'on'].includes(cleaned)) return true;
      if (['false', 'no', 'n', 'off'].includes(cleaned)) return false;
    }
    throw validationError(`${field} must be a boolean or recognized boolean string`);
  }

  function confidenceValue(value) {
    const cleaned = text(value, 'medium').toLowerCase();
    return ['low', 'medium', 'high'].includes(cleaned) ? cleaned : 'medium';
  }

  function reviewStatusValue(value) {
    const cleaned = text(value, 'draft').toLowerCase().replace(/ /g, '_');
    return ['draft', 'needs_review', 'reviewed', 'published'].includes(cleaned) ? cleaned : 'draft';
  }

  function round(value, places) {
    const factor = Math.pow(10, places);
    const rounded = Math.round((Math.abs(value) + Number.EPSILON) * factor) / factor;
    return Object.is(value, -0) || value < 0 ? -rounded : rounded;
  }

  function safePercent(numerator, denominator) {
    return denominator === 0 ? null : (numerator / denominator) * 100;
  }

  function normalizeInput(data) {
    const source = data || {};
    return {
      initiative: text(source.initiative, 'Untitled initiative'),
      goal: text(source.goal, 'Clarify impact goal'),
      sdg_theme: text(source.sdg_theme, 'Sustainable development'),
      indicator: text(source.indicator, 'Indicator'),
      unit: text(source.unit, 'units'),
      baseline_value: number(source.baseline_value, 'baseline_value', 0),
      current_value: number(source.current_value, 'current_value', 0),
      target_value: number(source.target_value, 'target_value', 100),
      baseline_period: text(source.baseline_period, 'baseline'),
      current_period: text(source.current_period, 'current'),
      source: text(source.source, ''),
      method_notes: text(source.method_notes, ''),
      confidence: confidenceValue(source.confidence),
      review_status: reviewStatusValue(source.review_status),
      beneficiaries: optionalInteger(source.beneficiaries, 'beneficiaries', 0),
      budget_usd: optionalNumber(source.budget_usd, 'budget_usd', 0),
      higher_is_better: booleanValue(source.higher_is_better, 'higher_is_better', true)
    };
  }

  function progress(record) {
    if (record.higher_is_better) {
      return safePercent(record.current_value - record.baseline_value, record.target_value - record.baseline_value);
    }
    return safePercent(record.baseline_value - record.current_value, record.baseline_value - record.target_value);
  }

  function status(progressValue, record) {
    if (progressValue === null || !Number.isFinite(progressValue)) return 'needs baseline/target review';
    const prefix = record.review_status === 'draft' || record.review_status === 'needs_review' ? 'draft — ' : 'reviewed — ';
    if (record.confidence === 'low') return prefix + 'interpret cautiously';
    if (progressValue >= 100) return prefix + 'target reached or exceeded';
    if (progressValue >= 75) return prefix + 'near target';
    if (progressValue >= 40) return prefix + 'partial progress';
    if (progressValue >= 0) return prefix + 'early progress';
    return prefix + 'moving away from target';
  }

  function qualityComponents(record) {
    return {
      source_documented: record.source ? 25 : 0,
      method_documented: record.method_notes.length >= 20 ? 25 : 0,
      confidence_signal: record.confidence === 'high' ? 25 : record.confidence === 'medium' ? 15 : 5,
      review_signal: record.review_status === 'reviewed' || record.review_status === 'published' ? 25 : record.review_status === 'needs_review' ? 10 : 0
    };
  }

  function buildImpactRecord(raw, generatedAt) {
    const record = normalizeInput(raw);
    const absoluteChange = record.current_value - record.baseline_value;
    const percentChange = safePercent(absoluteChange, record.baseline_value);
    const rawProgress = progress(record);
    const progressValue = rawProgress === null || !Number.isFinite(rawProgress) ? null : round(rawProgress, 2);
    const remainingGap = record.higher_is_better ? record.target_value - record.current_value : record.current_value - record.target_value;
    const costPerBeneficiary = record.beneficiaries !== null && record.beneficiaries > 0 && record.budget_usd !== null
      ? round(record.budget_usd / record.beneficiaries, 2)
      : null;
    const components = qualityComponents(record);
    const notes = [
      `${record.indicator} changed from ${record.baseline_value} ${record.unit} in ${record.baseline_period} to ${record.current_value} ${record.unit} in ${record.current_period}.`,
      'Progress should be interpreted against the indicator definition, data source, method notes, confidence level, and review status.',
      progressValue === null
        ? 'Progress to target could not be calculated because the baseline and target need review.'
        : `Estimated progress to target is ${progressValue.toFixed(2)}%.`
    ];
    if (record.confidence === 'low') {
      notes.push('Confidence is low, so this record should be treated as preliminary until the source and method are reviewed.');
    }
    if (record.review_status === 'draft' || record.review_status === 'needs_review') {
      notes.push('Review status indicates that this output is not final.');
    }

    return {
      record_type: 'global_impact_catalyst_record',
      generated_at: generatedAt || new Date().toISOString(),
      initiative: record.initiative,
      goal: record.goal,
      sdg_theme: record.sdg_theme,
      indicator: record.indicator,
      unit: record.unit,
      baseline_period: record.baseline_period,
      current_period: record.current_period,
      baseline_value: record.baseline_value,
      current_value: record.current_value,
      target_value: record.target_value,
      higher_is_better: record.higher_is_better,
      source: record.source,
      method_notes: record.method_notes,
      confidence: record.confidence,
      review_status: record.review_status,
      beneficiaries: record.beneficiaries,
      budget_usd: record.budget_usd,
      metrics: {
        absolute_change: round(absoluteChange, 4),
        percent_change_from_baseline: percentChange === null ? null : round(percentChange, 2),
        progress_to_target_percent: progressValue,
        remaining_gap: round(remainingGap, 4),
        status: status(progressValue, record),
        cost_per_beneficiary_usd: costPerBeneficiary,
        data_quality_score: Math.min(100, Object.values(components).reduce(function (sum, value) { return sum + value; }, 0)),
        data_quality_components: components
      },
      interpretation_notes: notes,
      traceability_path: TRACEABILITY_PATH.slice(),
      boundaries: BOUNDARIES.slice()
    };
  }

  function escapeHtml(value) {
    return String(value).replace(/[&<>'"]/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' })[char];
    });
  }

  function clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  function formInput(form) {
    const data = new FormData(form);
    return {
      initiative: data.get('initiative'),
      goal: data.get('goal'),
      sdg_theme: data.get('sdgTheme'),
      indicator: data.get('indicator'),
      unit: data.get('unit'),
      higher_is_better: data.get('higherIsBetter'),
      baseline_period: data.get('baselinePeriod'),
      current_period: data.get('currentPeriod'),
      baseline_value: data.get('baseline'),
      current_value: data.get('current'),
      target_value: data.get('target'),
      beneficiaries: data.get('beneficiaries'),
      budget_usd: data.get('budget'),
      confidence: data.get('confidence'),
      review_status: data.get('reviewStatus'),
      source: data.get('source'),
      method_notes: data.get('method')
    };
  }

  function render(rootElement, record) {
    const progressElement = rootElement.querySelector('[data-gic-progress]');
    const qualityElement = rootElement.querySelector('[data-gic-quality]');
    const statusElement = rootElement.querySelector('[data-gic-status]');
    const bar = rootElement.querySelector('[data-gic-bar]');
    const result = rootElement.querySelector('[data-gic-result]');
    const jsonElement = rootElement.querySelector('[data-gic-json]');
    const progressValue = record.metrics.progress_to_target_percent;

    progressElement.textContent = progressValue === null ? 'n/a' : `${progressValue}%`;
    qualityElement.textContent = `${record.metrics.data_quality_score}/100`;
    statusElement.textContent = record.metrics.status;
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
      <p><strong>Completeness/review signal:</strong> ${record.metrics.data_quality_score}/100. This is not an objective evidence-quality rating.</p>
    `;
    jsonElement.textContent = JSON.stringify(record, null, 2);
  }

  function setExample(form) {
    const mapping = {
      initiative: example.initiative,
      goal: example.goal,
      sdgTheme: example.sdg_theme,
      indicator: example.indicator,
      unit: example.unit,
      higherIsBetter: String(example.higher_is_better),
      baselinePeriod: example.baseline_period,
      currentPeriod: example.current_period,
      baseline: example.baseline_value,
      current: example.current_value,
      target: example.target_value,
      beneficiaries: example.beneficiaries,
      budget: example.budget_usd,
      confidence: example.confidence,
      reviewStatus: example.review_status,
      source: example.source,
      method: example.method_notes
    };
    Object.keys(mapping).forEach(function (key) {
      if (form.elements[key]) form.elements[key].value = mapping[key];
    });
  }

  function showError(rootElement, form, message) {
    const summary = rootElement.querySelector('[data-gic-errors]');
    summary.hidden = false;
    summary.textContent = message;
    summary.focus();
    const invalid = form.querySelector(':invalid');
    if (invalid) invalid.setAttribute('aria-invalid', 'true');
  }

  function clearError(rootElement, form) {
    const summary = rootElement.querySelector('[data-gic-errors]');
    summary.hidden = true;
    summary.textContent = '';
    form.querySelectorAll('[aria-invalid="true"]').forEach(function (field) { field.removeAttribute('aria-invalid'); });
  }

  function download(record) {
    const blob = new Blob([JSON.stringify(record, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'global-impact-catalyst-record.json';
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  }

  function initializeBrowser() {
    if (typeof document === 'undefined') return;
    document.querySelectorAll('[data-gic-demo]').forEach(function (rootElement) {
      if (rootElement.dataset.gicInitialized === 'true') return;
      rootElement.dataset.gicInitialized = 'true';
      const form = rootElement.querySelector('[data-gic-form]');
      let currentRecord;

      function generate() {
        clearError(rootElement, form);
        if (!form.reportValidity()) {
          showError(rootElement, form, 'Please complete the required fields and correct invalid values.');
          return null;
        }
        try {
          currentRecord = buildImpactRecord(formInput(form));
          render(rootElement, currentRecord);
          return currentRecord;
        } catch (error) {
          showError(rootElement, form, error && error.message ? error.message : 'The record could not be generated.');
          return null;
        }
      }

      currentRecord = generate();
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        generate();
      });
      rootElement.querySelector('[data-gic-reset]').addEventListener('click', function () {
        setExample(form);
        generate();
      });
      rootElement.querySelector('[data-gic-download]').addEventListener('click', function () {
        const record = generate();
        if (record) download(record);
      });
    });
  }

  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initializeBrowser);
    else initializeBrowser();
  }

  return {
    ENGINE_VERSION: '1.0.1',
    normalizeInput: normalizeInput,
    buildImpactRecord: buildImpactRecord,
    example: example
  };
}));
