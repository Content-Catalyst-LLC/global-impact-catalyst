(function(){'use strict';
function request(root,path,options){options=options||{};options.headers=Object.assign({'X-WP-Nonce':root.dataset.nonce,'Content-Type':'application/json'},options.headers||{});return fetch(root.dataset.rest+path,options).then(function(r){return r.json().then(function(v){if(!r.ok)throw new Error(v.message||'Request failed');return v;});});}
function values(root){var out={};root.querySelectorAll('input[name]').forEach(function(i){out[i.name]=i.value.trim();});return out;}
function show(root,value){root.querySelector('[data-gic-analysis-results]').textContent=JSON.stringify(value,null,2);}
document.addEventListener('click',function(e){var root=e.target.closest('[data-gic-analysis-studio]');if(!root)return;var v=values(root),action=null,path='',body=null;
if(e.target.matches('[data-gic-analysis-load]')){path='analysis-repository?workspace_id='+encodeURIComponent(v.workspace_id);}
if(e.target.matches('[data-gic-analysis-trend]')){path='analysis-trends';body=v;}
if(e.target.matches('[data-gic-analysis-benchmark]')){path='analysis-benchmarks';body=Object.assign({},v,{name:'Reference benchmark',value:0,unit_id:'count'});}
if(e.target.matches('[data-gic-analysis-uncertainty]')){path='analysis-uncertainty-models';body={workspace_id:v.workspace_id,name:'Planning range',uncertainty_type:'relative',relative_margin_percent:10};}
if(e.target.matches('[data-gic-analysis-scenario]')){path='analysis-scenarios';body=Object.assign({},v,{name:'Planning scenario',model_type:'linear',periods:3,unit_id:'count',parameters:{period_change:0}});}
if(!path)return;e.preventDefault();action=body?{method:'POST',body:JSON.stringify(body)}:{};request(root,path,action).then(function(x){show(root,x);}).catch(function(err){show(root,{error:err.message});});});
})();
