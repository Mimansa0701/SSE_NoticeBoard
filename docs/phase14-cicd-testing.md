# Phase 14: CI/CD and Security Testing

## CI/CD Pipeline
Implemented GitHub Actions workflow (`.github/workflows/ci.yml`). 
**Workflow stages:** Checkout -> Install dependencies -> Run Bandit (SAST) -> Run pytest -> Build Docker Verification.

## Testing Strategy
- **Unit Tests:** Verified application models and routing logic in `test_app.py`.
- **Integration Tests:** Database and Flask view integration tests validating RBAC access in `test_app.py`.
- **End-to-End Test:** Added `test_e2e_full_workflow` in `test_advanced.py` to trace the user journey from login -> create notice -> dashboard -> logout.
- **Fuzzing / Robustness:** Added `test_fuzz_notice_input` in `test_advanced.py` to ensure extremely large payloads (10k+ characters) do not cause 500 Internal Server errors.
- **Security Defect / Remediation:** Added `test_xss_protection` simulating an XSS payload injected into the notice title. The remediation relies on Jinja2's auto-escaping, completely neutering the attack vector (script tags become encoded HTML entities).