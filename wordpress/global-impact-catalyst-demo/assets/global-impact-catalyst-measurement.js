(function () {
  'use strict';

  const config = window.GICMeasurementConfig || {};
  const root = String(config.restRoot || '').replace(/\/?$/, '/');

  function request(path, options) {
    const settings = Object.assign({ headers: {} }, options || {});
    settings.headers = Object.assign({ 'X-WP-Nonce': config.nonce || '' }, settings.headers || {});
    if (settings.body && typeof settings.body !== 'string') {
      settings.headers['Content-Type'] = 'application/json';
      settings.body = JSON.stringify(settings.body);
    }
    return fetch(root + path.replace(/^\//, ''), settings).then(async (response) => {
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.message || 'The measurement request failed.');
      }
      return payload;
    });
  }

  function formObject(form) {
    const result = {};
    new FormData(form).forEach((value, key) => {
      const text = String(value).trim();
      if (text !== '') result[key] = text;
    });
    return result;
  }

  function numberOrNull(value) {
    if (value === undefined || value === null || value === '') return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function init(container) {
    const workspace = container.querySelector('[data-gic-measurement-workspace]');
    const initiative = container.querySelector('[data-gic-measurement-initiative]');
    const status = container.querySelector('[data-gic-measurement-status]');
    const summary = container.querySelector('[data-gic-measurement-summary]');
    const records = container.querySelector('[data-gic-measurement-records]');
    let current = null;

    function announce(message, isError) {
      status.textContent = message;
      status.classList.toggle('is-error', Boolean(isError));
    }

    function common(data) {
      data.workspace_id = workspace.value.trim();
      data.initiative_id = initiative.value.trim();
      if (!data.workspace_id) throw new Error('Enter a workspace ID.');
      if (!data.initiative_id) throw new Error('Enter an initiative ID.');
      return data;
    }

    function render(repository) {
      current = repository;
      const integrity = repository.integrity || {};
      summary.innerHTML = [
        ['Observations', integrity.observation_count || 0],
        ['Beneficiary definitions', integrity.beneficiary_definition_count || 0],
        ['Beneficiary observations', integrity.beneficiary_observation_count || 0],
        ['Financial records', integrity.financial_record_count || 0],
        ['Outcome portfolios', integrity.outcome_portfolio_count || 0],
        ['Aggregation runs', integrity.aggregation_run_count || 0]
      ].map(([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`).join('');

      const sections = [
        ['Recent observations', repository.observations || [], (item) => `${item.period_label}: ${item.value === null ? 'missing' : item.value} ${item.unit_id} · ${item.data_state}`],
        ['Beneficiaries', repository.beneficiary_definitions || [], (item) => `${item.name} · ${item.reach_type} · ${item.counting_method} · overlap ${item.overlap_policy}`],
        ['Financial records', repository.financial_records || [], (item) => `${item.period_label}: ${item.reporting_amount === null ? 'missing' : item.reporting_amount} ${item.reporting_currency} · ${item.record_type}`],
        ['Outcome portfolios', repository.outcome_portfolios || [], (item) => `${item.name} · ${item.aggregation_method} · ${(item.members || []).length} members`]
      ];
      records.innerHTML = sections.map(([title, items, describe]) => {
        const body = items.length ? `<ul>${items.slice(-12).map((item) => `<li>${describe(item)}</li>`).join('')}</ul>` : '<p>No records yet.</p>';
        return `<section><h3>${title}</h3>${body}</section>`;
      }).join('');
    }

    async function load() {
      const workspaceId = workspace.value.trim();
      if (!workspaceId) return announce('Enter a workspace ID.', true);
      announce('Loading measurement repository…');
      try {
        const repository = await request(`measurement-repository?workspace_id=${encodeURIComponent(workspaceId)}`);
        render(repository);
        announce(`Loaded measurement repository v${repository.repository_version}.`);
      } catch (error) {
        announce(error.message, true);
      }
    }

    container.querySelector('[data-gic-measurement-load]').addEventListener('click', load);
    container.querySelector('[data-gic-measurement-download]').addEventListener('click', () => {
      if (!current) return announce('Load a repository before downloading.', true);
      const blob = new Blob([JSON.stringify(current, null, 2) + '\n'], { type: 'application/json' });
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = `global-impact-measurement-${current.workspace_id || 'workspace'}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(link.href);
    });

    const bind = (selector, path, transform, success) => {
      const form = container.querySelector(selector);
      form.addEventListener('submit', async (event) => {
        event.preventDefault();
        try {
          const data = transform(formObject(form));
          announce('Saving…');
          const payload = await request(typeof path === 'function' ? path(data) : path, { method: 'POST', body: data });
          announce(success(payload));
          await load();
        } catch (error) {
          announce(error.message, true);
        }
      });
    };

    bind('[data-gic-observation-form]', 'observations', (data) => {
      common(data);
      data.value = numberOrNull(data.value);
      data.dimensions = {};
      if (data.geography) data.dimensions.geography = data.geography;
      if (data.population_group) data.dimensions.population_group = data.population_group;
      delete data.geography;
      delete data.population_group;
      return data;
    }, (payload) => `Saved observation ${payload.observation_record_id}.`);

    bind('[data-gic-beneficiary-form]', 'beneficiary-definitions', common, (payload) => `Saved beneficiary definition ${payload.beneficiary_definition_id}.`);

    bind('[data-gic-beneficiary-observation-form]', 'beneficiary-observations', (data) => {
      common(data);
      data.observed_count = numberOrNull(data.observed_count);
      data.overlap_estimate = numberOrNull(data.overlap_estimate);
      data.dimensions = data.age_band ? { age_band: data.age_band } : {};
      delete data.age_band;
      return data;
    }, (payload) => `Saved beneficiary observation ${payload.beneficiary_observation_id}.`);

    bind('[data-gic-financial-form]', 'financial-records', (data) => {
      common(data);
      data.amount = numberOrNull(data.amount);
      data.exchange_rate = numberOrNull(data.exchange_rate);
      return data;
    }, (payload) => `Saved financial record ${payload.financial_record_id}.`);

    bind('[data-gic-outcome-portfolio-form]', 'outcome-portfolios', (data) => {
      if (!workspace.value.trim()) throw new Error('Enter a workspace ID.');
      data.workspace_id = workspace.value.trim();
      return data;
    }, (payload) => `Created outcome portfolio ${payload.outcome_portfolio_id}.`);

    bind('[data-gic-outcome-member-form]', 'outcome-portfolio-members', (data) => {
      data.initiative_id = data.member_initiative_id || initiative.value.trim();
      delete data.member_initiative_id;
      return data;
    }, (payload) => `Added portfolio member ${payload.membership_id}.`);

    bind('[data-gic-outcome-aggregate-form]', (data) => `outcome-portfolios/${encodeURIComponent(data.outcome_portfolio_id)}/aggregate`, (data) => data, (payload) => `Aggregation complete: ${payload.value === null ? 'no compatible total' : payload.value}.`);
  }

  document.querySelectorAll('[data-gic-measurement-portfolio]').forEach(init);
}());
