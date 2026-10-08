# Phase 16: Final Security Review and Traceability

## Traceability Document

**Scenario:** "An unauthorized student attempts to modify or delete a faculty/admin notice."

1. **Requirement:** The system must enforce Role-Based Access Control (RBAC). Only Faculty and Admins can manage notices.
2. **Use Case:** Manage Notices.
3. **DFD:** External Entity (Student) -> Web App -> Notice Deletion Endpoint -> Database.
4. **Threat:** Elevation of Privilege (Spoofing/Tampering).
5. **Vulnerability:** Broken Access Control / Insecure Direct Object Reference (IDOR) on the notice ID endpoint.
6. **Attack Tree:** 
   - Gain unauthorized access to delete notice
     - Guess Notice ID
       - Send POST to `/notice/ID/delete`
         - Exploit missing RBAC check
7. **User Story:** As an Admin, I want to ensure that students cannot access deletion endpoints, so that notices cannot be tampered with.
8. **Sprint Task:** Implement `@roles_required` decorator for notice endpoints.
9. **Implementation:** See `auth.py: roles_required('ADMIN', 'FACULTY')`.
10. **Test:** See `test_app.py: test_student_cannot_create_notice()`.
11. **Deployment Control:** Logs generated for `UNAUTHORIZED_ACCESS_ATTEMPT` on failure, feeding to monitoring system.

## Highest Security Risks & Controls
1. **Broken Access Control (IDOR)** -> Mitigated by `@roles_required` and server-side session validation.
2. **Cross-Site Scripting (XSS)** -> Mitigated by automatic Jinja2 context-aware HTML escaping.
3. **Cross-Site Request Forgery (CSRF)** -> Mitigated by custom cryptographic `csrf_token` generation and validation for all state-changing operations.

## Project Limitations
1. Uses SQLite, which may not scale concurrently across multiple instances/pods without network-attached storage or a transition to PostgreSQL.
2. Passwords for default accounts are hardcoded in the `seed_db` function for demo purposes; they should be dynamically loaded via Secrets in production.