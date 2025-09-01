function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');}
function el(id){ return document.getElementById(id); }
async function api(path, method='GET', body){ 
  const res = await fetch(path, {method, headers:{'Content-Type':'application/json'}, body: body?JSON.stringify(body):undefined});
  if(!res.ok) throw new Error(await res.text()); return res.json();
}
async function genTokens(){ const r=await api('/tokens/generate','POST'); el('tools-out').textContent=r.stdout||r.stderr||JSON.stringify(r); }
async function reindex(){ const r=await api('/admin/reindex','POST'); el('tools-out').textContent=JSON.stringify(r,null,2); }
async function verify(){ const r=await api('/admin/verify','POST'); el('tools-out').textContent=JSON.stringify(r,null,2); }
async function ingest(){ const r=await api('/admin/ingest','POST'); el('tools-out').textContent=JSON.stringify(r,null,2); }
async function addAlert(){ const m=el('alert-msg').value.trim(); if(!m) return; const r=await api('/alerts','POST',{title:'Admin', message:m}); loadAlerts(); }
async function loadAlerts(){ const d=await api('/alerts'); const root=document.getElementById('alerts'); root.innerHTML=''; d.items.forEach(a=>{ const div=document.createElement('div'); div.className='alert'; div.innerHTML=`<strong>${esc(a.title)}</strong><div>${esc(a.message)}</div><small>${esc(a.ts)}</small>`; root.appendChild(div); }); }
async function loadFeedback(){ const d=await api('/feedback'); const root=document.getElementById('fb-list'); root.innerHTML=''; d.items.forEach(f=>{ const div=document.createElement('div'); div.className='alert'; div.innerHTML=`<div><em>${esc(f.type)}</em> — ${esc(f.value||f.text||'')}</div><small>${esc(f.ts)}</small>`; root.appendChild(div); }); }
document.addEventListener('DOMContentLoaded', ()=>{
  el('tok-gen').addEventListener('click', genTokens);
  el('reindex').addEventListener('click', reindex);
  el('verify').addEventListener('click', verify);
  el('ingest').addEventListener('click', ingest);
  el('alert-add').addEventListener('click', addAlert);
  loadAlerts(); loadFeedback();
});