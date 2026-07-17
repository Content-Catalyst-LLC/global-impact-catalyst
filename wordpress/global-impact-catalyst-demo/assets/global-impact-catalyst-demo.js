(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.GlobalImpactCatalystCore = api;
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const ENGINE_VERSION = '1.1.0';
  const CONTRACT_VERSION = '1.1.0';
  const SCHEMA_VERSION = '1.1.0';
  const CLAIM_TYPES = ['descriptive_observation', 'progress_to_target_statement', 'comparison', 'contribution_statement', 'causal_claim'];
  const DESIGN_TYPES = ['monitoring', 'before_after', 'comparison_group', 'quasi_experimental', 'randomized', 'qualitative', 'mixed_methods'];
  const TRACEABILITY_PATH = ['workspace', 'initiative', 'goal', 'outcome', 'indicator definition', 'baseline', 'observation', 'target', 'source', 'method', 'interpretation', 'claim', 'review', 'revision', 'publication'];
  const BOUNDARIES = [
    'This contract is not an ESG assurance opinion, SDG certification, regulatory filing, or audit finding.',
    'Derived progress does not establish causality, contribution, attribution, or comparative superiority.',
    'Claims depend on documented sources, method design, indicator definition, and human review.',
    'Validation checks contract consistency; it does not automatically verify truth or source authenticity.'
  ];
  const example = {
    workspace: 'Community Impact Portfolio',
    initiative: 'Community Energy Retrofit Pilot',
    goal: 'Reduce household energy burden while improving residential efficiency.',
    outcome: 'Participating households experience lower monthly energy costs.',
    sdg_theme: 'Affordable and clean energy',
    indicator: 'Average monthly bill reduction',
    indicator_definition: 'Mean reduction in monthly household utility bills relative to the baseline period.',
    unit: 'USD',
    higher_is_better: true,
    baseline_period: '2025 baseline',
    current_period: '2026 Q2',
    target_period: '2027',
    baseline_value: 0,
    current_value: 18,
    target_value: 30,
    beneficiaries: 420,
    population_group: 'Participating households',
    geography: 'Chicago, Illinois',
    budget_usd: 125000,
    budget_currency: 'USD',
    confidence: 'medium',
    review_status: 'needs_review',
    source: 'Pilot utility-billing sample and participant survey summary',
    source_locator: 'Internal pilot evidence package GIC-ENERGY-2026-Q2',
    method_name: 'Before-and-after billing comparison',
    method_version: '1.0',
    design_type: 'before_after',
    method_notes: 'Current value is the observed average monthly bill reduction across participating households compared with baseline average bills. Results should be reviewed for seasonality and household-size differences.',
    claim_type: 'progress_to_target_statement',
    claim_statement: ''
  };

  function validationError(message) {
    const error = new Error(message);
    error.name = 'InputValidationError';
    return error;
  }
  function text(value, fallback) { return String(value === null || typeof value === 'undefined' ? (fallback || '') : value).trim(); }
  function enumValue(value, allowed, fallback) {
    const cleaned = text(value, fallback).toLowerCase().replace(/ /g, '_').replace(/-/g, '_');
    return allowed.includes(cleaned) ? cleaned : fallback;
  }
  function numberValue(value, field, fallback) {
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
    const parsed = numberValue(value, field);
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
  function round(value, places) {
    const factor = Math.pow(10, places);
    const rounded = Math.round((Math.abs(value) + Number.EPSILON) * factor) / factor;
    return Object.is(value, -0) || value < 0 ? -rounded : rounded;
  }
  function canonicalNumber(value) { return value === null ? 'null' : String(value); }
  function utf8Bytes(value) {
    if (typeof TextEncoder !== 'undefined') return Array.from(new TextEncoder().encode(value));
    const encoded = unescape(encodeURIComponent(value));
    return Array.from(encoded).map(function (char) { return char.charCodeAt(0); });
  }
  function fnv1a(value) {
    let hash = 0x811c9dc5;
    utf8Bytes(value).forEach(function (byte) {
      hash ^= byte;
      hash = Math.imul(hash, 0x01000193) >>> 0;
    });
    return hash >>> 0;
  }
  function stableToken(value) { return fnv1a(value).toString(16).padStart(8, '0') + fnv1a('gic|' + value).toString(16).padStart(8, '0'); }
  function stableId(kind, seed) { return `gic-${kind}-${stableToken(kind + '|' + seed)}`; }
  function entity(kind, seed, timestamp, fields) {
    return Object.assign({ entity_type: kind, id: stableId(kind.replace(/_/g, '-'), seed), created_at: timestamp, updated_at: timestamp }, fields);
  }
  function normalizeInput(data) {
    const source = data || {};
    const unit = text(source.unit, '');
    const goal = text(source.goal, '');
    const sourceName = text(source.source, '');
    const currentPeriod = text(source.current_period, '');
    return {
      workspace: text(source.workspace, 'Default workspace'),
      initiative: text(source.initiative, ''),
      goal: goal,
      outcome: text(source.outcome, '') || goal,
      sdg_theme: text(source.sdg_theme, 'Sustainable development'),
      indicator: text(source.indicator, ''),
      indicator_definition: text(source.indicator_definition, '') || text(source.indicator, ''),
      unit: unit,
      baseline_unit: text(source.baseline_unit, '') || unit,
      current_unit: text(source.current_unit, '') || unit,
      target_unit: text(source.target_unit, '') || unit,
      baseline_value: numberValue(source.baseline_value, 'baseline_value', 0),
      current_value: numberValue(source.current_value, 'current_value', 0),
      target_value: numberValue(source.target_value, 'target_value', 100),
      baseline_period: text(source.baseline_period, ''),
      current_period: currentPeriod,
      target_period: text(source.target_period, '') || currentPeriod,
      source: sourceName,
      source_locator: text(source.source_locator, '') || sourceName,
      method_name: text(source.method_name, 'Entered measurement method'),
      method_notes: text(source.method_notes, ''),
      method_version: text(source.method_version, '1.0'),
      design_type: enumValue(source.design_type, DESIGN_TYPES, 'before_after'),
      confidence: enumValue(source.confidence, ['low', 'medium', 'high'], 'medium'),
      review_status: enumValue(source.review_status, ['draft', 'needs_review', 'reviewed', 'published'], 'draft'),
      beneficiaries: optionalInteger(source.beneficiaries, 'beneficiaries', 0),
      population_group: text(source.population_group, 'Affected population'),
      geography: text(source.geography, 'Not specified'),
      budget_usd: optionalNumber(source.budget_usd, 'budget_usd', 0),
      budget_currency: text(source.budget_currency, 'USD').toUpperCase(),
      higher_is_better: booleanValue(source.higher_is_better, 'higher_is_better', true),
      claim_type: enumValue(source.claim_type, CLAIM_TYPES, 'progress_to_target_statement'),
      claim_statement: text(source.claim_statement, ''),
      comparison_basis: text(source.comparison_basis, ''),
      contribution_rationale: text(source.contribution_rationale, ''),
      causal_design: text(source.causal_design, ''),
      record_id: text(source.record_id, ''),
      created_at: text(source.created_at, ''),
      updated_at: text(source.updated_at, '')
    };
  }
  function seedMaterial(input) {
    return [input.workspace, input.initiative, input.goal, input.outcome, input.sdg_theme, input.indicator, input.indicator_definition, input.unit,
      canonicalNumber(input.baseline_value), canonicalNumber(input.current_value), canonicalNumber(input.target_value), input.baseline_period,
      input.current_period, input.target_period, input.source, input.method_notes, input.claim_type].join('\x1f');
  }
  function safePercent(numerator, denominator) { return denominator === 0 ? null : (numerator / denominator) * 100; }
  function progress(input) {
    const raw = input.higher_is_better
      ? safePercent(input.current_value - input.baseline_value, input.target_value - input.baseline_value)
      : safePercent(input.baseline_value - input.current_value, input.baseline_value - input.target_value);
    return raw === null ? null : round(raw, 2);
  }
  function status(progressValue, input) {
    if (progressValue === null || !Number.isFinite(progressValue)) return 'needs baseline/target review';
    const prefix = ['draft', 'needs_review'].includes(input.review_status) ? 'draft — ' : 'reviewed — ';
    if (input.confidence === 'low') return prefix + 'interpret cautiously';
    if (progressValue >= 100) return prefix + 'target reached or exceeded';
    if (progressValue >= 75) return prefix + 'near target';
    if (progressValue >= 40) return prefix + 'partial progress';
    if (progressValue >= 0) return prefix + 'early progress';
    return prefix + 'moving away from target';
  }
  function qualityComponents(input) {
    return {
      source_documented: input.source ? 25 : 0,
      method_documented: input.method_notes.length >= 20 ? 25 : 0,
      confidence_signal: input.confidence === 'high' ? 25 : input.confidence === 'medium' ? 15 : 5,
      review_signal: ['reviewed', 'published'].includes(input.review_status) ? 25 : input.review_status === 'needs_review' ? 10 : 0
    };
  }
  function deriveMetrics(input) {
    const absolute = input.current_value - input.baseline_value;
    const percent = safePercent(absolute, input.baseline_value);
    const progressValue = progress(input);
    const gap = input.higher_is_better ? input.target_value - input.current_value : input.current_value - input.target_value;
    const cost = input.beneficiaries !== null && input.beneficiaries > 0 && input.budget_usd !== null ? round(input.budget_usd / input.beneficiaries, 2) : null;
    const components = qualityComponents(input);
    return {
      absolute_change: round(absolute, 4),
      percent_change_from_baseline: percent === null ? null : round(percent, 2),
      progress_to_target_percent: progressValue,
      remaining_gap: round(gap, 4),
      status: status(progressValue, input),
      cost_per_beneficiary: cost === null ? null : { value: cost, currency: input.budget_currency },
      data_quality_score: Math.min(Object.values(components).reduce(function (sum, value) { return sum + value; }, 0), 100),
      data_quality_components: components,
      calculation_method: {
        engine: 'global-impact-catalyst',
        engine_version: ENGINE_VERSION,
        rounding: 'decimal half up',
        progress_formula: 'direction-aware change from baseline divided by baseline-to-target distance'
      }
    };
  }
  function periodKey(label) {
    const yearMatch = label.match(/(?:^|\D)((?:19|20)\d{2})(?!\d)/);
    if (!yearMatch) return null;
    const quarterMatch = label.match(/\bQ([1-4])\b/i);
    return [Number(yearMatch[1]), quarterMatch ? Number(quarterMatch[1]) : 0];
  }
  function issue(severity, path, rule, message, remediation) {
    return { issue_id: `gic-issue-${stableToken([severity, path, rule, message].join('|'))}`, severity: severity, path: path, rule_id: rule, message: message, remediation: remediation };
  }
  function validateInput(input) {
    const issues = [];
    const required = [
      ['$.facts.initiative.name', input.initiative], ['$.facts.goal.statement', input.goal], ['$.facts.indicator.name', input.indicator],
      ['$.facts.indicator.definition.unit', input.unit], ['$.facts.measurement.baseline.period.label', input.baseline_period],
      ['$.facts.measurement.observations[0].period.label', input.current_period], ['$.facts.sources[0].title', input.source],
      ['$.facts.methods[0].description', input.method_notes]
    ];
    required.forEach(function (entry) {
      if (!entry[1]) issues.push(issue('error', entry[0], 'GIC-REQ-001', 'Required impact fact is missing.', 'Enter a specific value and regenerate the contract.'));
    });
    const units = [input.unit, input.baseline_unit, input.current_unit, input.target_unit];
    const normalized = Array.from(new Set(units.filter(Boolean).map(function (unit) { return unit.trim().toLowerCase(); })));
    if (normalized.length > 1) issues.push(issue('error', '$.facts.measurement', 'GIC-UNIT-001', 'Baseline, observation, target, and indicator units are not compatible.', 'Use one canonical unit or convert all values before calculating progress.'));
    if (units.some(function (unit) { return unit.includes('\n') || unit.length > 64; })) issues.push(issue('error', '$.facts.indicator.definition.unit', 'GIC-UNIT-002', 'Unit labels must be concise single-line values.', 'Use a recognized short unit label such as people, %, kg, kWh, or USD.'));
    const baselineKey = periodKey(input.baseline_period);
    const currentKey = periodKey(input.current_period);
    if (baselineKey && currentKey && (baselineKey[0] > currentKey[0] || (baselineKey[0] === currentKey[0] && baselineKey[1] > currentKey[1]))) {
      issues.push(issue('error', '$.facts.measurement', 'GIC-PERIOD-001', 'Baseline period occurs after the current observation period.', 'Correct the period labels or reverse the measurement roles.'));
    } else if (!baselineKey || !currentKey) {
      issues.push(issue('warning', '$.facts.measurement', 'GIC-PERIOD-002', 'Period ordering could not be verified from the labels.', 'Use labels containing an unambiguous four-digit year and optional quarter.'));
    }
    if (input.baseline_value === input.target_value) issues.push(issue('error', '$.facts.measurement.target.value', 'GIC-TARGET-001', 'Baseline and target values are equal, so progress to target is undefined.', 'Choose a target different from the baseline or omit the progress claim.'));
    else if (input.higher_is_better && input.target_value < input.baseline_value) issues.push(issue('error', '$.facts.measurement.target.value', 'GIC-DIRECTION-001', 'A higher-is-better indicator has a target below its baseline.', 'Change the direction to lower-is-better or correct the target.'));
    else if (!input.higher_is_better && input.target_value > input.baseline_value) issues.push(issue('error', '$.facts.measurement.target.value', 'GIC-DIRECTION-002', 'A lower-is-better indicator has a target above its baseline.', 'Change the direction to higher-is-better or correct the target.'));
    if (input.source && !input.source_locator) issues.push(issue('warning', '$.facts.sources[0].locator', 'GIC-SOURCE-001', 'Source is named but has no retrievable locator.', 'Add a URL, citation, file identifier, or repository location.'));
    if (input.method_notes && input.method_notes.length < 20) issues.push(issue('warning', '$.facts.methods[0].description', 'GIC-METHOD-001', 'Method description is too brief for reproducibility.', 'Describe population, collection procedure, calculation, exclusions, and limitations.'));
    if (input.claim_type === 'comparison') {
      if (!['comparison_group', 'quasi_experimental', 'randomized', 'mixed_methods'].includes(input.design_type)) issues.push(issue('error', '$.derived.claims[0].design_metadata.design_type', 'GIC-CLAIM-COMP-001', 'Comparison claims require a design with an explicit comparison basis.', 'Select comparison_group, quasi_experimental, randomized, or mixed_methods.'));
      if (!input.comparison_basis) issues.push(issue('error', '$.derived.claims[0].design_metadata.comparison_basis', 'GIC-CLAIM-COMP-002', 'Comparison basis is missing.', 'Name the comparator, benchmark, counterfactual, or reference group.'));
    } else if (input.claim_type === 'contribution_statement') {
      if (!input.contribution_rationale) issues.push(issue('error', '$.derived.claims[0].design_metadata.contribution_rationale', 'GIC-CLAIM-CONTRIB-001', 'Contribution statement lacks a documented rationale.', 'Describe the plausible mechanism, other contributors, and supporting evidence.'));
      if (input.design_type === 'monitoring') issues.push(issue('warning', '$.derived.claims[0].design_metadata.design_type', 'GIC-CLAIM-CONTRIB-002', 'Monitoring alone provides limited support for contribution language.', 'Use cautious wording or add comparative, qualitative, or theory-based evidence.'));
    } else if (input.claim_type === 'causal_claim') {
      if (!['quasi_experimental', 'randomized'].includes(input.design_type)) issues.push(issue('error', '$.derived.claims[0].design_metadata.design_type', 'GIC-CLAIM-CAUSAL-001', 'Causal claims require a quasi-experimental or randomized design.', 'Select an eligible design and document its assumptions, assignment, and analysis.'));
      if (!input.causal_design) issues.push(issue('error', '$.derived.claims[0].design_metadata.causal_design', 'GIC-CLAIM-CAUSAL-002', 'Causal design metadata is missing.', 'Document identification strategy, assignment process, controls, threats, and analysis.'));
      if (input.confidence !== 'high') issues.push(issue('error', '$.derived.claims[0].confidence', 'GIC-CLAIM-CAUSAL-003', 'Causal claims require high declared confidence.', 'Downgrade the claim or complete the evidence review needed for high confidence.'));
      if (!['reviewed', 'published'].includes(input.review_status)) issues.push(issue('error', '$.governance.reviews[0].status', 'GIC-CLAIM-CAUSAL-004', 'Causal claims cannot remain draft or needs-review.', 'Complete independent review before using causal language.'));
    }
    if (['comparison', 'contribution_statement', 'causal_claim'].includes(input.claim_type) && !input.claim_statement) issues.push(issue('error', '$.derived.claims[0].statement', 'GIC-CLAIM-001', 'Stronger claim types require an explicit claim statement.', 'Enter the exact sentence that evidence and review are intended to support.'));
    return issues;
  }
  function validationResult(issues) {
    return {
      valid: !issues.some(function (item) { return item.severity === 'error'; }),
      error_count: issues.filter(function (item) { return item.severity === 'error'; }).length,
      warning_count: issues.filter(function (item) { return item.severity === 'warning'; }).length,
      info_count: issues.filter(function (item) { return item.severity === 'info'; }).length,
      issues: issues
    };
  }
  function claimStatement(input, metrics) {
    if (input.claim_statement) return input.claim_statement;
    if (input.claim_type === 'descriptive_observation') return `${input.indicator} was observed at ${input.current_value} ${input.unit} in ${input.current_period}.`;
    if (metrics.progress_to_target_percent === null) return `Progress to target for ${input.indicator} could not be calculated from the entered baseline and target.`;
    return `Estimated progress to target for ${input.indicator} is ${metrics.progress_to_target_percent.toFixed(2)}%.`;
  }
  function buildImpactContract(raw, generatedAt) {
    const input = normalizeInput(raw);
    const timestamp = generatedAt || input.updated_at || input.created_at || new Date().toISOString();
    const createdAt = input.created_at || timestamp;
    const updatedAt = input.updated_at || timestamp;
    const seed = seedMaterial(input);
    const recordId = input.record_id || stableId('record', seed);
    const entitySeed = recordId;
    const metrics = deriveMetrics(input);
    const issues = validateInput(input);
    const validation = validationResult(issues);
    const workspace = entity('workspace', entitySeed, createdAt, { name: input.workspace });
    const initiative = entity('initiative', entitySeed, createdAt, { workspace_id: workspace.id, name: input.initiative });
    const goal = entity('goal', entitySeed, createdAt, { initiative_id: initiative.id, statement: input.goal, sdg_theme: input.sdg_theme });
    const outcome = entity('outcome', entitySeed, createdAt, { goal_id: goal.id, statement: input.outcome });
    const definition = entity('indicator_definition_version', entitySeed, createdAt, { version: '1.0', name: input.indicator_definition, unit: input.unit, direction: input.higher_is_better ? 'higher_is_better' : 'lower_is_better' });
    const indicator = entity('indicator', entitySeed, createdAt, { outcome_id: outcome.id, name: input.indicator, definition_version: definition });
    const source = entity('source', entitySeed, createdAt, { title: input.source, locator: input.source_locator, source_type: 'entered_source' });
    const method = entity('method', entitySeed, createdAt, { name: input.method_name, version: input.method_version, description: input.method_notes, design_type: input.design_type });
    const baseline = entity('baseline', entitySeed, createdAt, { indicator_id: indicator.id, value: input.baseline_value, unit: input.baseline_unit, period: { label: input.baseline_period }, source_ids: [source.id], method_id: method.id });
    const target = entity('target', entitySeed, createdAt, { indicator_id: indicator.id, value: input.target_value, unit: input.target_unit, period: { label: input.target_period }, direction: definition.direction });
    const observation = entity('observation', entitySeed, createdAt, { indicator_id: indicator.id, value: input.current_value, unit: input.current_unit, period: { label: input.current_period }, source_ids: [source.id], method_id: method.id });
    const population = entity('population_group', entitySeed, createdAt, { name: input.population_group, observed_count: input.beneficiaries });
    const geography = entity('geography', entitySeed, createdAt, { name: input.geography, geography_type: 'entered_label' });
    const budgets = input.budget_usd === null ? [] : [entity('budget_record', entitySeed, createdAt, { initiative_id: initiative.id, amount: input.budget_usd, currency: input.budget_currency, period: { label: input.current_period } })];
    const interpretationTexts = [
      `${input.indicator} changed from ${input.baseline_value} ${input.unit} in ${input.baseline_period} to ${input.current_value} ${input.unit} in ${input.current_period}.`,
      'Progress must be interpreted against the indicator definition, source, method, population, geography, confidence, and review status.',
      metrics.progress_to_target_percent === null ? 'Progress to target is unavailable because the baseline and target are not compatible.' : `Estimated progress to target is ${metrics.progress_to_target_percent.toFixed(2)}%.`
    ];
    if (input.confidence === 'low') interpretationTexts.push('Confidence is low; treat this contract as preliminary until source and method review is complete.');
    const interpretations = interpretationTexts.map(function (value, index) { return entity('interpretation', entitySeed + '|' + (index + 1), createdAt, { interpretation_type: 'metric_interpretation', text: value, evidence_refs: [baseline.id, observation.id, target.id] }); });
    const claimErrors = issues.filter(function (item) { return item.path.indexOf('$.derived.claims') === 0 && item.severity === 'error'; });
    const claim = entity('claim', entitySeed, createdAt, {
      claim_type: input.claim_type,
      statement: claimStatement(input, metrics),
      confidence: input.confidence,
      evidence_refs: [source.id, method.id, baseline.id, observation.id, target.id],
      design_metadata: { design_type: input.design_type, comparison_basis: input.comparison_basis, contribution_rationale: input.contribution_rationale, causal_design: input.causal_design },
      eligibility: { eligible: claimErrors.length === 0, blocking_issue_ids: claimErrors.map(function (item) { return item.issue_id; }) }
    });
    const review = entity('review', entitySeed, createdAt, { status: input.review_status, confidence: input.confidence, reviewer: 'not_recorded', notes: '' });
    const revision = entity('revision', entitySeed, createdAt, { revision_number: 1, reason: 'Initial canonical contract', parent_revision_id: null });
    const publications = input.review_status === 'published' ? [entity('publication', entitySeed, createdAt, { status: 'published', published_at: updatedAt, title: input.initiative })] : [];
    return {
      contract_type: 'global_impact_contract',
      contract_version: CONTRACT_VERSION,
      schema_version: SCHEMA_VERSION,
      record_id: recordId,
      created_at: createdAt,
      updated_at: updatedAt,
      lifecycle_status: input.review_status,
      provenance: {
        generated_by: { name: 'global-impact-catalyst', version: ENGINE_VERSION, runtime: 'cross-runtime' },
        input_fingerprint: stableToken(seed),
        source_contract_version: null,
        migration: null
      },
      facts: {
        workspace: workspace,
        initiative: initiative,
        goal: goal,
        outcomes: [outcome],
        indicator: indicator,
        measurement: { baseline: baseline, target: target, observations: [observation] },
        sources: [source],
        methods: [method],
        population_groups: [population],
        geographies: [geography],
        budget_records: budgets
      },
      derived: { metrics: metrics, interpretations: interpretations, claims: [claim] },
      governance: { reviews: [review], revisions: [revision], publications: publications },
      validation: validation,
      traceability_path: TRACEABILITY_PATH.slice(),
      boundaries: BOUNDARIES.slice()
    };
  }

  function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, function (char) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' })[char]; }); }
  function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
  function formInput(form) {
    const data = new FormData(form);
    return {
      workspace: data.get('workspace'), initiative: data.get('initiative'), goal: data.get('goal'), outcome: data.get('outcome'), sdg_theme: data.get('sdgTheme'),
      indicator: data.get('indicator'), indicator_definition: data.get('indicatorDefinition'), unit: data.get('unit'), higher_is_better: data.get('higherIsBetter'),
      baseline_period: data.get('baselinePeriod'), current_period: data.get('currentPeriod'), target_period: data.get('targetPeriod'), baseline_value: data.get('baseline'),
      current_value: data.get('current'), target_value: data.get('target'), beneficiaries: data.get('beneficiaries'), population_group: data.get('populationGroup'),
      geography: data.get('geography'), budget_usd: data.get('budget'), budget_currency: data.get('budgetCurrency'), confidence: data.get('confidence'),
      review_status: data.get('reviewStatus'), source: data.get('source'), source_locator: data.get('sourceLocator'), method_name: data.get('methodName'),
      method_version: data.get('methodVersion'), design_type: data.get('designType'), method_notes: data.get('method'), claim_type: data.get('claimType'),
      claim_statement: data.get('claimStatement'), comparison_basis: data.get('comparisonBasis'), contribution_rationale: data.get('contributionRationale'), causal_design: data.get('causalDesign')
    };
  }
  function render(rootElement, contract) {
    const metrics = contract.derived.metrics;
    const facts = contract.facts;
    const claim = contract.derived.claims[0];
    const validation = contract.validation;
    const progressElement = rootElement.querySelector('[data-gic-progress]');
    const qualityElement = rootElement.querySelector('[data-gic-quality]');
    const statusElement = rootElement.querySelector('[data-gic-status]');
    const bar = rootElement.querySelector('[data-gic-bar]');
    const result = rootElement.querySelector('[data-gic-result]');
    const jsonElement = rootElement.querySelector('[data-gic-json]');
    const progressValue = metrics.progress_to_target_percent;
    progressElement.textContent = progressValue === null ? 'n/a' : `${progressValue}%`;
    qualityElement.textContent = `${metrics.data_quality_score}/100`;
    statusElement.textContent = validation.valid ? metrics.status : `${validation.error_count} validation error${validation.error_count === 1 ? '' : 's'}`;
    bar.style.width = `${clamp(progressValue || 0, 0, 100)}%`;
    const issues = validation.issues.length ? `<div class="gic-demo__validation"><h4>Validation</h4><ul>${validation.issues.map(function (item) { return `<li data-severity="${escapeHtml(item.severity)}"><strong>${escapeHtml(item.rule_id)}</strong>: ${escapeHtml(item.message)} <span>${escapeHtml(item.remediation)}</span></li>`; }).join('')}</ul></div>` : '<p class="gic-demo__valid">Contract validation passed.</p>';
    result.innerHTML = `
      <p class="gic-demo__contract-version">Contract ${escapeHtml(contract.contract_version)} · <code>${escapeHtml(contract.record_id)}</code></p>
      <h3>${escapeHtml(facts.initiative.name || 'Untitled initiative')}</h3>
      <p><strong>Goal:</strong> ${escapeHtml(facts.goal.statement || 'No goal entered')}</p>
      <p><strong>Outcome:</strong> ${escapeHtml(facts.outcomes[0].statement || 'No outcome entered')}</p>
      <p><strong>Indicator:</strong> ${escapeHtml(facts.indicator.name)} (${escapeHtml(facts.indicator.definition_version.unit)})</p>
      <ul><li>Baseline: ${facts.measurement.baseline.value} ${escapeHtml(facts.measurement.baseline.unit)} (${escapeHtml(facts.measurement.baseline.period.label)})</li>
      <li>Current: ${facts.measurement.observations[0].value} ${escapeHtml(facts.measurement.observations[0].unit)} (${escapeHtml(facts.measurement.observations[0].period.label)})</li>
      <li>Target: ${facts.measurement.target.value} ${escapeHtml(facts.measurement.target.unit)} (${escapeHtml(facts.measurement.target.period.label)})</li>
      <li>Remaining gap: ${metrics.remaining_gap} ${escapeHtml(facts.indicator.definition_version.unit)}</li></ul>
      <p><strong>Claim:</strong> ${escapeHtml(claim.statement)} <em>(${claim.eligibility.eligible ? 'eligible under current rules' : 'blocked by validation'})</em></p>
      <p><strong>Source:</strong> ${escapeHtml(facts.sources[0].title || 'No source entered')}</p>${issues}`;
    jsonElement.textContent = JSON.stringify(contract, null, 2);
  }
  function setExample(form) {
    const mapping = {
      workspace: example.workspace, initiative: example.initiative, goal: example.goal, outcome: example.outcome, sdgTheme: example.sdg_theme,
      indicator: example.indicator, indicatorDefinition: example.indicator_definition, unit: example.unit, higherIsBetter: String(example.higher_is_better),
      baselinePeriod: example.baseline_period, currentPeriod: example.current_period, targetPeriod: example.target_period, baseline: example.baseline_value,
      current: example.current_value, target: example.target_value, beneficiaries: example.beneficiaries, populationGroup: example.population_group,
      geography: example.geography, budget: example.budget_usd, budgetCurrency: example.budget_currency, confidence: example.confidence,
      reviewStatus: example.review_status, source: example.source, sourceLocator: example.source_locator, methodName: example.method_name,
      methodVersion: example.method_version, designType: example.design_type, method: example.method_notes, claimType: example.claim_type,
      claimStatement: example.claim_statement, comparisonBasis: '', contributionRationale: '', causalDesign: ''
    };
    Object.keys(mapping).forEach(function (key) { if (form.elements[key]) form.elements[key].value = mapping[key]; });
  }
  function showError(rootElement, form, message) {
    const summary = rootElement.querySelector('[data-gic-errors]');
    summary.hidden = false; summary.textContent = message; summary.focus();
    const invalid = form.querySelector(':invalid'); if (invalid) invalid.setAttribute('aria-invalid', 'true');
  }
  function clearError(rootElement, form) {
    const summary = rootElement.querySelector('[data-gic-errors]'); summary.hidden = true; summary.textContent = '';
    form.querySelectorAll('[aria-invalid="true"]').forEach(function (field) { field.removeAttribute('aria-invalid'); });
  }
  function download(contract) {
    const blob = new Blob([JSON.stringify(contract, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob); const anchor = document.createElement('a'); anchor.href = url;
    anchor.download = 'global-impact-catalyst-contract-v1.1.0.json'; document.body.appendChild(anchor); anchor.click(); anchor.remove(); URL.revokeObjectURL(url);
  }
  function initializeBrowser() {
    if (typeof document === 'undefined') return;
    document.querySelectorAll('[data-gic-demo]').forEach(function (rootElement) {
      if (rootElement.dataset.gicInitialized === 'true') return;
      rootElement.dataset.gicInitialized = 'true';
      const form = rootElement.querySelector('[data-gic-form]'); let currentContract;
      function generate() {
        clearError(rootElement, form);
        if (!form.reportValidity()) { showError(rootElement, form, 'Please complete the required fields and correct invalid values.'); return null; }
        try { currentContract = buildImpactContract(formInput(form)); render(rootElement, currentContract); return currentContract; }
        catch (error) { showError(rootElement, form, error && error.message ? error.message : 'The contract could not be generated.'); return null; }
      }
      currentContract = generate();
      form.addEventListener('submit', function (event) { event.preventDefault(); generate(); });
      rootElement.querySelector('[data-gic-reset]').addEventListener('click', function () { setExample(form); generate(); });
      rootElement.querySelector('[data-gic-download]').addEventListener('click', function () { const contract = currentContract || generate(); if (contract) download(contract); });
    });
  }
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initializeBrowser); else initializeBrowser();
  }
  return {
    ENGINE_VERSION: ENGINE_VERSION,
    CONTRACT_VERSION: CONTRACT_VERSION,
    normalizeInput: normalizeInput,
    validateInput: validateInput,
    buildImpactContract: buildImpactContract,
    buildImpactRecord: buildImpactContract,
    stableToken: stableToken,
    example: example
  };
}));
