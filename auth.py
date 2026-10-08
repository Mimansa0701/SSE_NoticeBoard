from functools import wraps
from flask import session, redirect, url_for, flash, request, render_template
import secrets
from database import get_db

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def verify_csrf_token(token):
    session_token = session.get('csrf_token')
    if not session_token or not token or not secrets.compare_digest(session_token, token):
        return False
    return True

def log_audit(action, details="", user_id=None, username=None, db_path=None):
    if user_id is None:
        user_id = session.get('user_id')
    if username is None:
        username = session.get('username', 'ANONYMOUS')
    
    ip_address = request.remote_addr or '127.0.0.1'
    
    try:
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_logs (user_id, username, action, ip_address, details)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, action, ip_address, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Failed to write audit log: {e}")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                log_audit(
                    action='UNAUTHORIZED_ACCESS_ATTEMPT',
                    details=f"User '{session.get('username')}' with role '{user_role}' attempted to access restricted endpoint '{request.path}' requiring roles {allowed_roles}."
                )
                flash('Access Denied: You do not have permission to perform this action.', 'danger')
                return render_template('error.html', error_code=403, message='Forbidden: Insufficient privileges'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
