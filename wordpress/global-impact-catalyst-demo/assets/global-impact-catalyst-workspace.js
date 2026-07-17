(function () {
  'use strict';
  const config = window.GlobalImpactCatalystWorkspaceConfig || {};
  const core = window.GlobalImpactCatalystCore;
  if (!core || !config.restUrl) return;

  function api(path, options) {
    const settings = Object.assign({ headers: {} }, options || {});
    settings.headers = Object.assign({ 'X-WP-Nonce': config.nonce }, settings.headers || {});
    if (settings.body && typeof settings.body !== 'string') {
      settings.headers['Content-Type'] = 'application/json';
      settings.body = JSON.stringify(settings.body);
    }
    return fetch(config.restUrl + path, settings).then(async function (response) {
      const body = await response.json().catch(function () { return {}; });
      if (!response.ok) {
        const error = new Error(body.message || 'Repository request failed.');
        error.details = body.data || {};
        throw error;
      }
      return body;
    });
  }

  function contractToForm(form, contract) {
    const facts = contract.facts;
    const measurement = facts.measurement;
    const definition = facts.indicator.definition_version;
    const observation = measurement.observations[0];
    const source = facts.sources[0] || {};
    const method = facts.methods[0] || {};
    const population = facts.population_groups[0] || {};
    const geography = facts.geographies[0] || {};
    const budget = facts.budget_records[0] || {};
    const claim = contract.derived.claims[0] || {};
    const design = claim.design_metadata || {};
    const values = {
      workspace: facts.workspace.name, initiative: facts.initiative.name, goal: facts.goal.statement,
      outcome: (facts.outcomes[0] || {}).statement, sdgTheme: facts.goal.sdg_theme,
      indicator: facts.indicator.name, indicatorDefinition: definition.name, unit: definition.unit,
      higherIsBetter: String(definition.direction === 'higher_is_better'), baselinePeriod: measurement.baseline.period.label,
      currentPeriod: observation.period.label, targetPeriod: measurement.target.period.label,
      baseline: measurement.baseline.value, current: observation.value, target: measurement.target.value,
      beneficiaries: population.observed_count == null ? '' : population.observed_count,
      populationGroup: population.name || '', geography: geography.name || '',
      budget: budget.amount == null ? '' : budget.amount, budgetCurrency: budget.currency || 'USD',
      confidence: claim.confidence || 'medium', reviewStatus: contract.lifecycle_status || 'draft',
      source: source.title || '', sourceLocator: source.locator || '', methodName: method.name || '',
      methodVersion: method.version || '1.0', designType: method.design_type || 'before_after',
      method: method.description || '', claimType: claim.claim_type || 'progress_to_target_statement',
      claimStatement: claim.statement || '', comparisonBasis: design.comparison_basis || '',
      contributionRationale: design.contribution_rationale || '', causalDesign: design.causal_design || ''
    };
    Object.keys(values).forEach(function (name) {
      if (form.elements[name]) form.elements[name].value = values[name];
    });
  }

  function downloadJson(filename, value) {
    const blob = new Blob([JSON.stringify(value, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = filename; document.body.appendChild(anchor); anchor.click();
    anchor.remove(); URL.revokeObjectURL(url);
  }

  document.querySelectorAll('[data-gic-workspace]').forEach(function (root) {
    const demo = root.querySelector('[data-gic-demo]');
    const form = demo.querySelector('[data-gic-form]');
    const list = root.querySelector('[data-gic-workspace-list]');
    const status = root.querySelector('[data-gic-workspace-status]');
    const search = root.querySelector('[data-gic-workspace-search]');
    const includeArchived = root.querySelector('[data-gic-workspace-archived]');
    let current = null;
    let autosaveTimer = null;

    function announce(message, isError) {
      status.textContent = message;
      status.dataset.state = isError ? 'error' : 'ok';
    }

    function rawContract() {
      const raw = core.formInput(form);
      if (current && current.contract) {
        raw.record_id = current.contract.record_id;
        raw.created_at = current.contract.created_at;
      }
      return core.buildImpactContract(raw);
    }

    function renderCurrent(contract) {
      contractToForm(form, contract);
      core.render(demo, contract);
    }

    function refreshList() {
      const params = new URLSearchParams();
      if (search.value.trim()) params.set('search', search.value.trim());
      if (includeArchived.checked) params.set('include_archived', 'true');
      return api('records?' + params.toString()).then(function (records) {
        list.innerHTML = '';
        if (!records.length) {
          list.innerHTML = '<p>No saved initiatives match this view.</p>';
          return;
        }
        records.forEach(function (record) {
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'gic-workspace__record';
          if (record.archived_at) button.classList.add('is-archived');
          button.innerHTML = '<strong></strong><span></span>';
          button.querySelector('strong').textContent = record.initiative_name || 'Untitled initiative';
          button.querySelector('span').textContent = (record.workspace_name || 'Workspace') + ' · revision ' + record.revision + (record.archived_at ? ' · archived' : '');
          button.addEventListener('click', function () { openRecord(record.record_id); });
          list.appendChild(button);
        });
      }).catch(function (error) { announce(error.message, true); });
    }

    function openRecord(recordId) {
      api('records/' + encodeURIComponent(recordId)).then(function (record) {
        current = record;
        const contract = record.autosave && Number(record.autosave.base_revision) === Number(record.revision)
          ? record.autosave.contract : record.contract;
        current.contract = contract;
        renderCurrent(contract);
        announce('Opened ' + (contract.facts.initiative.name || 'initiative') + ' at revision ' + record.revision + (record.autosave ? ' with a recoverable autosave.' : '.'));
      }).catch(function (error) { announce(error.message, true); });
    }

    function saveContract(contract, expectedRevision) {
      return api('records?expected_revision=' + Number(expectedRevision || 0), { method: 'POST', body: contract }).then(function (result) {
        current = Object.assign({}, result.repository, { contract: result.contract, archived_at: null });
        renderCurrent(result.contract);
        announce('Saved revision ' + result.repository.revision + '.');
        refreshList();
        return result;
      });
    }

    function save() {
      try {
        saveContract(rawContract(), current ? current.revision : 0).catch(function (error) {
          const actual = error.details && error.details.actual_revision;
          announce(error.message + (actual != null ? ' Current repository revision: ' + actual + '.' : ''), true);
        });
      } catch (error) { announce(error.message, true); }
    }

    function autosave() {
      if (!current || current.archived_at) return;
      try {
        const contract = rawContract();
        api('autosaves?base_revision=' + Number(current.revision), { method: 'POST', body: contract })
          .then(function () { announce('Draft autosaved against revision ' + current.revision + '.'); })
          .catch(function (error) { announce(error.message, true); });
      } catch (error) { announce(error.message, true); }
    }

    form.addEventListener('input', function () {
      clearTimeout(autosaveTimer);
      autosaveTimer = setTimeout(autosave, 900);
    });
    search.addEventListener('input', function () { clearTimeout(search._timer); search._timer = setTimeout(refreshList, 250); });
    includeArchived.addEventListener('change', refreshList);
    root.querySelector('[data-gic-workspace-refresh]').addEventListener('click', refreshList);
    root.querySelector('[data-gic-workspace-save]').addEventListener('click', save);
    root.querySelector('[data-gic-workspace-new]').addEventListener('click', function () {
      current = null; core.setExample(form); const contract = core.buildImpactContract(core.formInput(form)); renderCurrent(contract);
      announce('New unsaved initiative.');
    });
    root.querySelector('[data-gic-workspace-duplicate]').addEventListener('click', function () {
      if (!current) { announce('Open or save an initiative before duplicating it.', true); return; }
      const name = window.prompt('Name the duplicated initiative:', form.elements.initiative.value + ' — Copy');
      if (!name) return;
      const raw = core.formInput(form); raw.initiative = name; delete raw.record_id; delete raw.created_at;
      const contract = core.buildImpactContract(raw);
      current = null;
      saveContract(contract, 0).catch(function (error) { announce(error.message, true); });
    });
    root.querySelector('[data-gic-workspace-archive]').addEventListener('click', function () {
      if (!current) { announce('Open a saved initiative first.', true); return; }
      const restoring = Boolean(current.archived_at);
      api('records/' + encodeURIComponent(current.record_id) + '?expected_revision=' + current.revision + '&restore=' + (restoring ? 'true' : 'false'), { method: 'PUT' })
        .then(function (result) { current.revision = result.revision; current.archived_at = result.archived ? new Date().toISOString() : null; announce(result.archived ? 'Initiative archived.' : 'Initiative restored.'); refreshList(); })
        .catch(function (error) { announce(error.message, true); });
    });
    root.querySelector('[data-gic-workspace-export]').addEventListener('click', function () {
      try {
        const contract = rawContract();
        downloadJson('global-impact-catalyst-' + (contract.record_id || 'initiative') + '.json', contract);
        announce('Canonical contract exported.');
      } catch (error) { announce(error.message, true); }
    });
    root.querySelector('[data-gic-workspace-import]').addEventListener('change', function (event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      file.text().then(function (text) {
        const documentValue = JSON.parse(text);
        const contract = documentValue.contract_type === 'global_impact_contract' ? documentValue : core.buildImpactContract(documentValue);
        current = null; renderCurrent(contract);
        return saveContract(contract, 0);
      }).then(function () { announce('Imported and saved canonical contract.'); })
        .catch(function (error) { announce('Import failed: ' + error.message, true); });
      event.target.value = '';
    });

    refreshList();
  });
}());
