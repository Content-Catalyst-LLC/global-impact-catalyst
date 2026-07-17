(function () {
  'use strict';
  const config = window.GlobalImpactCatalystEvidenceConfig || {};
  const request = async (path, options) => {
    const response = await fetch((config.restUrl || '') + path, Object.assign({headers:{'Content-Type':'application/json','X-WP-Nonce':config.nonce || ''}}, options || {}));
    const body = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(body.message || 'Evidence repository request failed.');
    return body;
  };
  const formObject = form => Object.fromEntries(Array.from(new FormData(form).entries()).filter(([,value]) => String(value).trim() !== ''));
  const escapeHtml = value => String(value == null ? '' : value).replace(/[&<>'"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
  document.querySelectorAll('[data-gic-evidence-ledger]').forEach(root => {
    const status = root.querySelector('[data-gic-evidence-status]');
    const summary = root.querySelector('[data-gic-evidence-summary]');
    const records = root.querySelector('[data-gic-evidence-records]');
    const initiative = root.querySelector('[data-gic-evidence-initiative]');
    let currentChain = null;
    const setStatus = (message, error) => { status.textContent = message; status.dataset.state = error ? 'error' : 'ready'; };
    const render = chain => {
      currentChain = chain;
      const integrity = chain.integrity || {};
      summary.innerHTML = `<strong>${integrity.source_count || 0} sources</strong><span>${integrity.evidence_count || 0} evidence items</span><span>${integrity.dataset_count || 0} datasets</span><span>${integrity.edge_count || 0} provenance edges</span><span>${integrity.claim_link_count || 0} claim links</span><span>${integrity.contradicting_link_count || 0} contradictions</span>`;
      const sourceCards = (chain.sources || []).map(item => `<article><h4>${escapeHtml(item.title)}</h4><p>${escapeHtml(item.locator || 'No locator')}</p><code>${escapeHtml(item.source_id)}</code><small>License: ${escapeHtml(item.license || 'not_recorded')} · Version ${escapeHtml(item.current_version || 0)}</small></article>`).join('');
      const evidenceCards = (chain.evidence_items || []).map(item => `<article><h4>${escapeHtml(item.title || item.evidence_type)}</h4><p>${escapeHtml(item.exact_quote || item.paraphrase || item.notes)}</p><code>${escapeHtml(item.evidence_id)}</code><small>${escapeHtml(item.locator || '')}</small></article>`).join('');
      records.innerHTML = `<section><h3>Sources</h3>${sourceCards || '<p>No sources found.</p>'}</section><section><h3>Evidence</h3>${evidenceCards || '<p>No captured evidence.</p>'}</section>`;
    };
    const load = async () => {
      const id = initiative.value.trim(); if (!id) { setStatus('Enter an initiative ID.', true); return; }
      setStatus('Loading evidence chain…');
      try { const chain = await request('evidence-chain/' + encodeURIComponent(id)); render(chain); setStatus('Evidence chain loaded.'); }
      catch (error) { setStatus(error.message, true); }
    };
    root.querySelector('[data-gic-evidence-load]').addEventListener('click', load);
    root.querySelector('[data-gic-evidence-download]').addEventListener('click', () => {
      if (!currentChain) { setStatus('Load an evidence chain before exporting.', true); return; }
      const blob = new Blob([JSON.stringify(currentChain,null,2)+'\n'],{type:'application/json'}); const url=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=url; a.download='global-impact-evidence-chain.json'; a.click(); URL.revokeObjectURL(url);
    });
    const bind = (selector, path, after) => root.querySelector(selector).addEventListener('submit', async event => {
      event.preventDefault(); setStatus('Saving…');
      try { const result=await request(path,{method:'POST',body:JSON.stringify(formObject(event.currentTarget))}); setStatus('Saved.'); if (after) after(result,event.currentTarget); if (initiative.value.trim()) await load(); }
      catch (error) { setStatus(error.message,true); }
    });
    bind('[data-gic-source-form]','sources',(result,form)=>{ form.querySelector('[name="initiative_id"]').value=result.initiative_id || ''; initiative.value=result.initiative_id || initiative.value; });
    bind('[data-gic-evidence-form]','evidence');
    bind('[data-gic-dataset-form]','datasets');
    bind('[data-gic-claim-link-form]','claim-evidence');
  });
})();
