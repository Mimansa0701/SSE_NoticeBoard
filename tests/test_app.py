import pytest
import os
import sqlite3
from app import app
from database import init_db, seed_db
from config import Config

@pytest.fixture
def client():
    # Setup testing config
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Use an in-memory DB or temporary file
    db_path = os.path.join(Config.DATABASE_PATH + '_test.db')
    
    # Init DB
    with app.test_client() as client:
        with app.app_context():
            # Seed tests
            seed_db()
        yield client

def test_login_page_loads(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_successful_login(client):
    # Need to simulate CSRF token since we're not using Flask-WTF natively but custom logic
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
        
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'AdminPass123!',
        'csrf_token': 'test-token'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Notice Board' in response.data

def test_failed_login(client):
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
        
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'WrongPassword!',
        'csrf_token': 'test-token'
    }, follow_redirects=True)
    
    assert b'Invalid username or password' in response.data

def test_access_dashboard_without_login(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in to access this page.' in response.data

def test_student_cannot_create_notice(client):
    # Login as student
    with client.session_transaction() as sess:
        sess['csrf_token'] = 'test-token'
        
    client.post('/login', data={
        'username': 'student_cs',
        'password': 'StudentPass123!',
        'csrf_token': 'test-token'
    })
    
    # Attempt to access create notice
    response = client.get('/notice/create', follow_redirects=True)
    assert response.status_code == 403
    assert b'Forbidden: Insufficient privileges' in response.data
