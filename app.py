import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database import init_db, seed_db, get_db
from models import UserModel, NoticeModel, AuditLogModel
from auth import generate_csrf_token, verify_csrf_token, login_required, roles_required, log_audit
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database exists
init_db()
seed_db()

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf_token())

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if not verify_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token.', 'danger')
            return redirect(url_for('login'))
            
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = UserModel.get_by_username(username)
        
        if user and UserModel.verify_password(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            session['department'] = user['department']
            
            log_audit('LOGIN_SUCCESS', f"User {username} logged in successfully.", user['id'], user['username'])
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            log_audit('LOGIN_FAILED', f"Failed login attempt for username: {username}")
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    username = session.get('username')
    if user_id:
        log_audit('LOGOUT', f"User {username} logged out.", user_id, username)
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_role = session.get('user_role')
    user_dept = session.get('department')
    
    department_filter = request.args.get('department', 'All')
    category_filter = request.args.get('category', 'All')
    search_query = request.args.get('search', '')
    
    notices = NoticeModel.get_all_notices(
        user_role=user_role,
        user_dept=user_dept,
        department_filter=department_filter,
        category_filter=category_filter,
        search_query=search_query
    )
    
    return render_template('dashboard.html', notices=notices, user_role=user_role, user_dept=user_dept)

@app.route('/notice/create', methods=['GET', 'POST'])
@login_required
@roles_required('ADMIN', 'FACULTY')
def create_notice():
    if request.method == 'POST':
        if not verify_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token.', 'danger')
            return redirect(url_for('create_notice'))
            
        title = request.form.get('title')
        content = request.form.get('content')
        department = request.form.get('department')
        category = request.form.get('category')
        priority = request.form.get('priority')
        scheduled_at = request.form.get('scheduled_at')
        
        notice_id = NoticeModel.create(
            title=title, content=content, department=department,
            category=category, priority=priority,
            created_by=session['user_id'], creator_username=session['username'],
            scheduled_at=scheduled_at
        )
        
        log_audit('CREATE_NOTICE', f"Created notice ID {notice_id}", session['user_id'], session['username'])
        flash('Notice created successfully.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('notice_form.html', action='Create')

@app.route('/notice/<int:notice_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('ADMIN', 'FACULTY')
def edit_notice(notice_id):
    notice = NoticeModel.get_by_id(notice_id)
    if not notice:
        flash('Notice not found.', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        if not verify_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token.', 'danger')
            return redirect(url_for('edit_notice', notice_id=notice_id))
            
        title = request.form.get('title')
        content = request.form.get('content')
        department = request.form.get('department')
        category = request.form.get('category')
        priority = request.form.get('priority')
        scheduled_at = request.form.get('scheduled_at')
        
        NoticeModel.update(
            notice_id=notice_id, title=title, content=content,
            department=department, category=category,
            priority=priority, scheduled_at=scheduled_at
        )
        
        log_audit('EDIT_NOTICE', f"Edited notice ID {notice_id}", session['user_id'], session['username'])
        flash('Notice updated successfully.', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('notice_form.html', action='Edit', notice=notice)

@app.route('/notice/<int:notice_id>/delete', methods=['POST'])
@login_required
@roles_required('ADMIN', 'FACULTY')
def delete_notice(notice_id):
    if not verify_csrf_token(request.form.get('csrf_token')):
        flash('Invalid CSRF token.', 'danger')
        return redirect(url_for('dashboard'))
        
    NoticeModel.delete(notice_id)
    log_audit('DELETE_NOTICE', f"Deleted notice ID {notice_id}", session['user_id'], session['username'])
    flash('Notice deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/audit_logs')
@login_required
@roles_required('ADMIN')
def audit_logs():
    search = request.args.get('search', '')
    logs = AuditLogModel.get_all(search=search)
    return render_template('audit_logs.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
