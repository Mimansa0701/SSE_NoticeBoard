from database import get_db
from werkzeug.security import check_password_hash
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
            scheduled_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
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
        conn.close()

    @staticmethod
    def delete(notice_id, db_path=None):
        conn = get_db(db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE notices SET is_active = 0 WHERE id = ?', (notice_id,))
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
        return logs
