import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from config import Config

def get_db(db_path=None):
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    conn = get_db(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        department TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        department TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'Normal',
        created_by INTEGER NOT NULL,
        creator_username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scheduled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_id INTEGER,
        username TEXT,
        action TEXT NOT NULL,
        ip_address TEXT,
        details TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def seed_db(db_path=None):
    init_db(db_path)
    conn = get_db(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM users')
    user_count = cursor.fetchone()['count']
    
    if user_count == 0:
        demo_users = [
            ('admin', generate_password_hash('AdminPass123!'), 'ADMIN', 'General'),
            ('faculty_cs', generate_password_hash('FacultyPass123!'), 'FACULTY', 'Computer Science'),
            ('faculty_ee', generate_password_hash('FacultyPass123!'), 'FACULTY', 'Electrical Engineering'),
            ('student_cs', generate_password_hash('StudentPass123!'), 'STUDENT', 'Computer Science'),
            ('student_ee', generate_password_hash('StudentPass123!'), 'STUDENT', 'Electrical Engineering')
        ]
        cursor.executemany('''
            INSERT INTO users (username, password_hash, role, department)
            VALUES (?, ?, ?, ?)
        ''', demo_users)
        conn.commit()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', ('faculty_cs',))
        faculty_cs_id = cursor.fetchone()['id']
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        admin_id = cursor.fetchone()['id']
        
        now = datetime.now()
        past_time = (now - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        future_time = (now + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')
        
        demo_notices = [
            (
                'End-Semester Examination Schedule Fall 2026',
                'The final examination schedule for all departments has been published. Please check your student portal for room assignments and timings.',
                'All', 'Exam', 'High', admin_id, 'admin', past_time, past_time
            ),
            (
                'CS402 Software Security Assignment 3 Released',
                'Assignment 3 focusing on Web Security, CSRF, and RBAC implementation is now active. Submission deadline is next Friday at 11:59 PM.',
                'Computer Science', 'Academic', 'Normal', faculty_cs_id, 'faculty_cs', past_time, past_time
            ),
            (
                'Annual Tech Symposium 2026 Registration',
                'Registration for the annual inter-college technology symposium is now open. Submit your project proposals by the end of this week.',
                'Computer Science', 'Event', 'Normal', faculty_cs_id, 'faculty_cs', past_time, past_time
            ),
            (
                '[UPCOMING] Scheduled Maintenance of Lab Workstations',
                'This notice is scheduled for future publication. Lab computers in CS Block B will undergo OS upgrade and security hardening.',
                'Computer Science', 'Urgent', 'Urgent', faculty_cs_id, 'faculty_cs', past_time, future_time
            )
        ]
        
        cursor.executemany('''
            INSERT INTO notices (title, content, department, category, priority, created_by, creator_username, created_at, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', demo_notices)
        
        cursor.execute('''
            INSERT INTO audit_logs (username, action, ip_address, details)
            VALUES ('SYSTEM', 'SYSTEM_INITIALIZATION', '127.0.0.1', 'Database initialized and seeded with demo accounts and notices.')
        ''')
        
        conn.commit()
    conn.close()
