# Contained mock API v1

Single-threaded HTTPS, `127.0.0.1:8443`, TLS 1.3, mTLS CERT_REQUIRED.
CA validates the chain/validity; SHA-256 DER fingerprint selects a pre-enrolled
actor. A client-supplied role or actor is never authentication. Unknown certificate,
expired application session (600 seconds), revoked membership → refusal.
Every request uses current server-side membership, including after role changes.

| Method / path | Action | Permission |
| --- | --- | --- |
| GET `/` | Local UI | enrolled member |
| GET `/app.js`, `/style.css` | Fixed assets | enrolled member |
| GET `/api/session` | Own actor, role, lab ID | enrolled member |
| POST `/api/execute` | Fixed mock operation | viewer: status; operator/admin: all four |
| POST `/api/audit` | Read sanitized events; body exactly `{}` | enrolled member |
| POST `/api/members` | Change role or revoke pre-enrolled member | lab-admin |

Execute schema: [CORE-CONTRACT.md](CORE-CONTRACT.md). Management schema:
`target`, `role` (viewer/operator/lab-admin or null), `request_id`, `issued_at`,
`lab_id`; no other/duplicate fields. Only pre-enrolled actors are eligible.
Admin cannot change/revoke self. Cross-lab requests are refused. Accepted management
IDs share the replay table; audit uses set_viewer/set_operator/set_lab_admin/revoke_member
with target in agent_id. Recovery reapplies completed role changes.

Host must be exactly `127.0.0.1:<port>`. If Origin is supplied it must match that
HTTPS origin. No CORS, cookies, bearer storage, localStorage or external assets.
POST requires one Content-Length (0–4096), no Transfer-Encoding, exact JSON MIME.
Headers bounded to 8192 after parsing; stdlib parser also has its own hard limits.
TLS handshake/read timeout 3 seconds; one processing thread; backlog 5. POST budget
100 requests per actor per server run. No unlimited agents/queues/payloads.
Audit has 1000 records and replay table 1000 IDs by default, hard limits in core.

Success: 200 JSON. Refusal: 403 `{"error":"fixed_reason_code"}`; internal storage
failure: 503 generic diagnostic. TLS refusal may occur before an HTTP response.
Logs never include headers, raw paths, certificates, keys or request bodies.
Auth failures at TLS/application boundary are not included in the core journal;
accepted/denied authorized mock and membership actions are audited.

Server runtime reads only the owner-private `/run/lab` configuration/journal and
fixed packaged UI assets. No command execution, dynamic loading or agent filesystem
access. Certificate creation is trusted provisioning, outside the API.
A single enrolled client may exhaust its bounded request/audit budget; no HA or
production availability promises. Admin/OS-owner compromise remains out of scope.
