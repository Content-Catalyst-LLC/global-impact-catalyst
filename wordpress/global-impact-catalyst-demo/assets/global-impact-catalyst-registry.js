(function () {
  'use strict';
  const config = window.GICRegistryConfig || {};
  const root = String(config.restRoot || '').replace(/\/$/, '') + '/';

  function request(path, options) {
    const settings = Object.assign({ headers: {} }, options || {});
    settings.headers = Object.assign({ 'X-WP-Nonce': config.nonce || '' }, settings.headers || {});
    if (settings.body && typeof settings.body !== 'string') {
      settings.headers['Content-Type'] = 'application/json';
      settings.body = JSON.stringify(settings.body);
    }
    return fetch(root + path.replace(/^\//, ''), settings).then(async function (response) {
      const payload = await response.json().catch(function () { return {}; });
      if (!response.ok) throw new Error(payload.message || 'Registry request failed.');
      return payload;
    });
  }

  function formObject(form) {
    const result = {};
    new FormData(form).forEach(function (value, key) {
      if (value === '') return;
      if (['target_value', 'benchmark_value', 'rolling_periods', 'relative_change_percent', 'lower_value', 'upper_value', 'start_value', 'end_value'].includes(key)) {
        result[key] = Number(value);
      } else result[key] = value;
    });
    return result;
  }

  function card(title, items, key) {
    const rows = (items || []).map(function (item) {
      const name = item.name || item.code || item[key] || 'Untitled';
      const detail = item.unit_id || item.dimension || item.method_type || item.target_type || item.design_type || '';
      return '<li><strong>' + escapeHtml(name) + '</strong>' + (detail ? '<span>' + escapeHtml(detail) + '</span>' : '') + '</li>';
    }).join('');
    return '<article><h3>' + escapeHtml(title) + '</h3><ul>' + (rows || '<li><span>No records yet.</span></li>') + '</ul></article>';
  }

  function escapeHtml(value) {
    return String(value == null ? '' : value).replace(/[&<>'"]/g, function (char) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char];
    });
  }

  document.querySelectorAll('[data-gic-indicator-registry]').forEach(function (container) {
    const workspace = container.querySelector('[data-gic-registry-workspace]');
    const status = container.querySelector('[data-gic-registry-status]');
    const summary = container.querySelector('[data-gic-registry-summary]');
    const records = container.querySelector('[data-gic-registry-records]');
    let current = null;

    function workspaceId() {
      const value = String(workspace.value || '').trim();
      if (!value) throw new Error('Enter a workspace ID first.');
      return value;
    }

    function render(registry) {
      current = registry;
      const integrity = registry.integrity || {};
      summary.innerHTML = [
        ['Units', integrity.unit_count || 0],
        ['Indicators', integrity.indicator_definition_count || 0],
        ['Baselines', integrity.baseline_model_count || 0],
        ['Targets', integrity.target_model_count || 0],
        ['Methods', integrity.method_definition_count || 0],
        ['Bindings', integrity.binding_count || 0]
      ].map(function (entry) { return '<div><span>' + entry[0] + '</span><strong>' + entry[1] + '</strong></div>'; }).join('');
      records.innerHTML = card('Units', registry.units, 'unit_id') +
        card('Indicator definitions', registry.indicator_definitions, 'indicator_definition_id') +
        card('Baseline models', registry.baseline_models, 'baseline_model_id') +
        card('Target models', registry.target_models, 'target_model_id') +
        card('Method definitions', registry.method_definitions, 'method_definition_id');
      status.textContent = integrity.valid === false ? 'Registry loaded with integrity issues.' : 'Registry loaded and structurally consistent.';
    }

    function load() {
      status.textContent = 'Loading registry…';
      return request('indicator-registry?workspace_id=' + encodeURIComponent(workspaceId())).then(render).catch(function (error) {
        status.textContent = error.message;
      });
    }

    container.querySelector('[data-gic-registry-load]').addEventListener('click', load);
    container.querySelector('[data-gic-registry-download]').addEventListener('click', function () {
      if (!current) { status.textContent = 'Load a registry before downloading.'; return; }
      const blob = new Blob([JSON.stringify(current, null, 2) + '\n'], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'global-impact-indicator-registry-' + current.workspace_id + '.json';
      link.click();
      URL.revokeObjectURL(link.href);
    });

    const forms = [
      ['[data-gic-unit-form]', 'units'],
      ['[data-gic-indicator-form]', 'indicator-definitions'],
      ['[data-gic-baseline-form]', 'baseline-models'],
      ['[data-gic-target-form]', 'target-models'],
      ['[data-gic-method-form]', 'method-definitions']
    ];
    forms.forEach(function (entry) {
      const form = container.querySelector(entry[0]);
      form.addEventListener('submit', function (event) {
        event.preventDefault();
        let body;
        try { body = Object.assign(formObject(form), { workspace_id: workspaceId() }); }
        catch (error) { status.textContent = error.message; return; }
        status.textContent = 'Saving governed record…';
        request(entry[1], { method: 'POST', body: body }).then(function () {
          form.reset();
          return load();
        }).catch(function (error) { status.textContent = error.message; });
      });
    });
  });
}());
