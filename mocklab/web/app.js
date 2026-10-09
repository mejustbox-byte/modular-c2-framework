'use strict';
let session;
const out = document.getElementById('result');
async function post(path, data) {
  const response = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data), cache:'no-store'});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'request_failed');
  return result;
}
function envelope() { return {request_id:crypto.randomUUID().replaceAll('-',''), issued_at:Date.now()/1000, lab_id:session.lab_id}; }
async function show(action) {
  try { out.textContent = JSON.stringify(await action(), null, 2); }
  catch (error) { out.textContent = String(error.message); }
}
document.querySelectorAll('[data-op]').forEach(button => button.addEventListener('click', () => show(() => {
  const request = {...envelope(), schema_version:1, agent_id:'mock-1', operation:button.dataset.op};
  if (request.operation === 'emit_test_event') request.fixture_id = 'synthetic-login';
  return post('/api/execute', request);
})));
document.getElementById('audit').addEventListener('click', () => show(async () => {
  const result = await post('/api/audit', {});
  document.getElementById('events').textContent = JSON.stringify(result.events, null, 2);
  return {audit_records:result.events.length};
}));
document.getElementById('apply').addEventListener('click', () => show(() => {
  const role = document.getElementById('role').value;
  return post('/api/members', {...envelope(), target:document.getElementById('target').value, role:role === 'revoke' ? null : role});
}));
(async () => {
  try {
    const response = await fetch('/api/session', {cache:'no-store'});
    if (!response.ok) throw new Error('identity_unavailable');
    session = await response.json();
    document.getElementById('identity').textContent = `${session.actor_id} · ${session.role} · ${session.lab_id}`;
    document.getElementById('membership').hidden = session.role !== 'lab-admin';
    if (session.role === 'viewer') document.querySelectorAll('[data-op]').forEach(b => {b.disabled = b.dataset.op !== 'status';});
  } catch (error) {out.textContent = error.message; document.querySelectorAll('button').forEach(b => {b.disabled = true;});}
})();
