(function(){
  'use strict';
  function request(root,path,options){
    options=options||{};options.headers=Object.assign({'Content-Type':'application/json','X-WP-Nonce':root.dataset.nonce||''},options.headers||{});
    return fetch((root.dataset.rest||'')+path,options).then(function(response){return response.json().then(function(body){if(!response.ok){throw new Error(body.message||'Request failed');}return body;});});
  }
  function text(value){return String(value==null?'':value).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c];});}
  function render(root,data){
    var integrity=data.integrity||{};
    root.querySelector('[data-gic-review-count="assignments"]').textContent=integrity.assignment_count||0;
    root.querySelector('[data-gic-review-count="open"]').textContent=(integrity.open_comment_count||0)+(integrity.open_correction_count||0);
    root.querySelector('[data-gic-review-count="publications"]').textContent=integrity.publication_count||0;
    var list=root.querySelector('[data-gic-review-list]');
    var items=[];
    (data.review_assignments||[]).slice().reverse().forEach(function(item){items.push('<div class="gic-review__item"><strong>'+text(item.status.replace(/_/g,' '))+'</strong> · '+text(item.subject_type)+'<small>'+text(item.reviewer_id)+' · '+text(item.priority)+' priority</small></div>');});
    (data.publications||[]).slice().reverse().forEach(function(item){items.push('<div class="gic-review__item"><strong>'+text(item.title)+'</strong><small>Publication: '+text(item.publication_status)+'</small></div>');});
    list.innerHTML=items.length?items.join(''):'<p class="gic-review__empty">No review assignments or publications yet.</p>';
  }
  function init(root){
    var status=root.querySelector('[data-gic-review-status]');
    function setStatus(message,error){status.textContent=message||'';status.className='gic-review__status'+(error?' gic-review__notice--error':'');}
    function load(){var workspace=root.querySelector('[name="workspace_id"]').value.trim();if(!workspace){setStatus('Enter a workspace ID to load the workflow.',true);return;}setStatus('Loading…');request(root,'review-workflow?workspace_id='+encodeURIComponent(workspace)).then(function(data){render(root,data);setStatus('Workflow loaded.');}).catch(function(error){setStatus(error.message,true);});}
    root.querySelector('[data-gic-review-load]').addEventListener('click',load);
    root.querySelector('[data-gic-review-assignment]').addEventListener('submit',function(event){event.preventDefault();var form=new FormData(event.currentTarget),payload={workspace_id:form.get('workspace_id'),initiative_id:form.get('initiative_id'),subject_type:'contract',subject_id:form.get('subject_id'),reviewer_id:form.get('reviewer_id'),role_id:form.get('role_id'),priority:form.get('priority')};setStatus('Creating assignment…');request(root,'review-assignments',{method:'POST',body:JSON.stringify(payload)}).then(function(){setStatus('Review assignment created.');load();}).catch(function(error){setStatus(error.message,true);});});
    root.querySelector('[data-gic-review-assessment]').addEventListener('submit',function(event){event.preventDefault();var form=new FormData(event.currentTarget),payload={workspace_id:form.get('workspace_id'),initiative_id:form.get('initiative_id'),assignment_id:form.get('assignment_id'),assessor_id:form.get('assessor_id'),dimensions:[{key:'evidence',score:Number(form.get('evidence_score')),maximum_score:100},{key:'method',score:Number(form.get('method_score')),maximum_score:100},{key:'traceability',score:Number(form.get('traceability_score')),maximum_score:100}]};setStatus('Saving assessment…');request(root,'quality-assessments',{method:'POST',body:JSON.stringify(payload)}).then(function(data){setStatus('Quality assessment saved: '+data.score+'/100.');load();}).catch(function(error){setStatus(error.message,true);});});
  }
  document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('[data-gic-review]').forEach(init);});
})();
