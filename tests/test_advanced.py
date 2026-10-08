import pytest
import os
from app import app
from database import seed_db
from config import Config

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            seed_db()
        yield client

# End-to-End Test
def test_e2e_full_workflow(client):
    # 1. Login as faculty
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
    
    login_resp = client.post('/login', data={
        'username': 'faculty_cs',
        'password': 'FacultyPass123!',
        'csrf_token': 'test-token'
    }, follow_redirects=True)
    assert b'Notice Board' in login_resp.data
    
    # 2. Create notice
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
        
    create_resp = client.post('/notice/create', data={
        'title': 'E2E Notice Title',
        'content': 'E2E Notice Content',
        'department': 'Computer Science',
        'category': 'Academic',
        'priority': 'High',
        'scheduled_at': '',
        'csrf_token': 'test-token'
    }, follow_redirects=True)
    assert b'Notice created successfully' in create_resp.data
    
    # 3. View dashboard
    dashboard_resp = client.get('/dashboard', follow_redirects=True)
    assert b'E2E Notice Title' in dashboard_resp.data
    
    # 4. Logout
    logout_resp = client.get('/logout', follow_redirects=True)
    assert b'You have been logged out' in logout_resp.data

# Fuzzing / Input Robustness
def test_fuzz_notice_input(client):
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
    
    client.post('/login', data={'username': 'faculty_cs', 'password': 'FacultyPass123!', 'csrf_token': 'test-token'})
    
    # Send giant payload (10,000 characters)
    giant_string = "A" * 10000
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
        
    resp = client.post('/notice/create', data={
        'title': 'Fuzz Title',
        'content': giant_string,
        'department': 'Computer Science',
        'category': 'Academic',
        'priority': 'High',
        'scheduled_at': '',
        'csrf_token': 'test-token'
    }, follow_redirects=True)
    
    # Should not crash (e.g. 500 error), should handle it smoothly (either truncate or save)
    assert resp.status_code == 200

# Security Defect / Remediation Test (XSS)
def test_xss_protection(client):
    # Attempt to inject a script tag
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
    client.post('/login', data={'username': 'faculty_cs', 'password': 'FacultyPass123!', 'csrf_token': 'test-token'})
    
    xss_payload = "<script>alert('XSS')</script>"
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
        
    client.post('/notice/create', data={
        'title': xss_payload,
        'content': 'Content',
        'department': 'General',
        'category': 'Event',
        'priority': 'Normal',
        'scheduled_at': '',
        'csrf_token': 'test-token'
    }, follow_redirects=True)
    
    dashboard_resp = client.get('/dashboard')
    
    # Jinja2 auto-escapes HTML, so the raw script tag should NOT be present.
    # It should be converted to &lt;script&gt;
    assert b"<script>alert('XSS')</script>" not in dashboard_resp.data
    assert b"&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;" in dashboard_resp.data