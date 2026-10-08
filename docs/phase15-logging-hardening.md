# Phase 15: Logging, Monitoring, and Hardening

## Audit Logging Events
The application successfully logs the following critical events in the `audit_logs` table:
1. `LOGIN_SUCCESS` (with username and IP)
2. `LOGIN_FAILED` (no passwords stored in logs)
3. `UNAUTHORIZED_ACCESS_ATTEMPT` (RBAC violations)
4. `CREATE_NOTICE` / `EDIT_NOTICE` / `DELETE_NOTICE`
5. `LOGOUT`
Logs do *not* capture credentials, tokens, or sensitive personal data.

## Security & Operational Metrics (Proposed)
1. **Failed Login Count (Threshold):** >5 in 10 minutes indicates brute-forcing.
2. **Unauthorized Access Attempts:** Highlights potential insider threat or enumeration.
3. **5xx Server Errors:** Indicates potential DoS attacks, uncaught exceptions, or system failure.
4. **Suspicious Input Attempts (XSS/SQLi keywords):** Metrics drawn from WAF/logs.
5. **Application Availability:** Uptime and latency monitoring.

## Security Hardening Checklist
- [x] **Authentication:** Implemented secure session handling. No default insecure passwords allowed in production.
- [x] **Authorization/RBAC:** Enforced at backend (`@roles_required`).
- [x] **Input Validation:** Required fields enforced; fuzzing passed.
- [x] **XSS Protection:** Enforced via Jinja2 template auto-escaping.
- [x] **CSRF Protection:** Tokens generated dynamically via `secrets` and verified on every POST.
- [x] **Secure Sessions:** Sessions configured with `SESSION_COOKIE_HTTPONLY = True` and `SESSION_COOKIE_SAMESITE = 'Lax'`.
- [x] **Password Hashing:** Enabled using `werkzeug.security` (PBKDF2/scrypt).
- [x] **Audit Logging:** Implemented server-side audit trails for actions.
- [x] **Docker Security:** Dropped root user, created `appuser`.
- [x] **Kubernetes Security:** `runAsNonRoot: true`, `allowPrivilegeEscalation: false`, dropped all capabilities.

## Secure Deployment Considerations
- Use TLS/HTTPS for all external communication.
- Restrict network access to the database using Kubernetes Network Policies.
- Use a secrets manager (e.g., HashiCorp Vault, K8s Secrets) instead of hardcoding environment variables.