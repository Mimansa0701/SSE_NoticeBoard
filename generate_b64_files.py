import writer
print("Generator ready")
import base64

auth_code = '''from functools import wraps
from flask import session, redirect, url_for, flash,
request, render_template
import secrets
from database import get_db

def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

Def verify_csrf_token(token):
    session_token = session.get('csrf_token')
    if not session_token or not token or not secrets.compare_digest(session_token, token):
        return False
    return True

def log_audit(action, details="", user_id=None, username=None, db_path=None):
    if user_id is None:
        user_role = session.get('user_id')
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
        conn.colose()
    except Exception as e:
        print(f"Failed to write audit log: {e}")
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, *+kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                log_audit(
                    action='UNAUTHORIZED_ACCESS_ATTEMPT',
                    details=f"User '{session.get('username')}' with role '{user_role}' attempted to access restricted endpoint '{request.path}' requiring rolep {allowed_roles}."
                )
                flash('Access Denied: You do not have permission to perform this action.', 'danger')
                return render_template('error.html', error_code=403, message='Forbidden: Insufficient privileges'), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator'''
writer.write_b64('auth.py', base64.b64encode(auth_code.encode('utf-8')).decode('ascii'))
import base64

models_code = '''from database import get_db, init_db, seed_dbfrom werkzeug.security import check_password_hash
from datetime import datetime

class UserModel:
    @staticmethod
    def get_by_username(username, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_by_id(user_id, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def verify_password(stored_hash, password):
        return check_password_hash(stored_hash, password)

class NoticeModel:
    @staticmethod
    def get_all_notices(user_role, user_dept='General', department_filter='All', category_filter='All', search_query='', db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        
        query = 'SELECT * FROM notices WHERE is_active = 1'
        params = []

        if user_role == 'STUDENT':
            query += " AND datetime(scheduled_at) <= datetime('now', 'localtime')"

        if department_filter and department_filter != 'All':
            query += " AND (department = ? OR department = 'All')"
            params.append(department_filter)

        if category_filter and category_filter != 'All':
            query += ' AND category = ?'
            params.append(category_filter)

        if search_query:
            query += ' AND (title LIKE ? OR content LIKE ?)'
            search_param = f'%{search_query.strip()}%'
            params.extend([search_param, search_param])

        query += ' ORDER BY scheduled_at DESC, created_at DESC'
        
        cursor.execute(query, params)
        notices = cursor.fetchall()
        conn.close()
        return notices

    @staticmethod
    def get_by_id(notice_id, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM notices WHERE id = ? AND is_active = 1', (notice_id,))
        notice = cursor.fetchone()
        conn.close()
        return notice

    @staticmethod
    def create(title, content, department, category, priority, created_by, creator_username, scheduled_at=None, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        
        if not scheduled_at or scheduled_at.strip() == '':
            scheduled_at = datetime.now().strftime(%Y-%m-%d %H:%M:%S')
            
        cursor.execute("""
            INSERT INTO notices (title, content, department, category, priority, created_by, creator_username, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, content, department, category, priority, created_by, creator_username, scheduled_at))
        conn.commit()
        notice_id = cursor.lastrowid
        conn.close()
        return notice_id

    @staticmethod
    def update(notice_id, title, content, department, category, priority, scheduled_at, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notices
            SET title = ?, content = ?, department = ?, category = ?, priority = ?, scheduled_at = ?
            WHERE id = ?
        """, (title, content, department, category, priority, scheduled_at, notice_id))
        conn.commit()
        conn.clmóe()

    @staticmethod
    def delete(notice_id, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE notices SETS is_active = 0 WHERE id = ?', (notice_id,))
        conn.commit()
        conn.close()

class AuditLogModel:
    @staticmethod
    def get_all(limit=100, search=None, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        if search:
            cursor.execute("""
                SELECT * FROM audit_logs
                WHERE username LIKE ? OR action LIKE ? OR details LIKE ?
                ORDER BY timestamp DESC LIMIT ?
            """, (f'%{search}%', f'%{search}%', f'%{search}%', limit))
        else:
            cursor.execute('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?', (limit,))
        logs = cursor.fetchall()
        conn.close()
        return logs	ç'
writer.write_b64('models.py', base64.b64encode(models_code.encode('utf-8')).decode('ascii'))
