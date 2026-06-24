from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'placement_system_secret_key_2024'

DB_PATH = 'placement.db'

# ─────────────────────────────────────────
#  DATABASE SETUP
# ─────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        branch TEXT,
        cgpa REAL,
        resume_link TEXT,
        skills TEXT,
        registered_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        role TEXT,
        package TEXT,
        eligibility_cgpa REAL DEFAULT 6.0,
        branches TEXT,
        last_date TEXT,
        location TEXT,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        company_id INTEGER,
        status TEXT DEFAULT 'Applied',
        applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(company_id) REFERENCES companies(id),
        UNIQUE(student_id, company_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    # Create default admin if not exists
    admin_pass = hashlib.sha256('admin123'.encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?, ?)", ('admin', admin_pass))

    # Add sample companies
    sample = [
        ('TCS', 'Tata Consultancy Services – leading IT company.', 'Software Engineer', '3.5 LPA', 6.0, 'CSE,IT,ECE', '2024-05-31', 'Pune'),
        ('Infosys', 'Global IT consulting firm.', 'Systems Engineer', '3.6 LPA', 6.5, 'CSE,IT,ECE,EEE', '2024-06-15', 'Bangalore'),
        ('Wipro', 'Technology and outsourcing company.', 'Project Engineer', '3.5 LPA', 6.0, 'CSE,IT,Mech,Civil', '2024-06-20', 'Hyderabad'),
        ('Accenture', 'Global professional services company.', 'Associate Software Engineer', '4.5 LPA', 7.0, 'CSE,IT,ECE', '2024-07-01', 'Mumbai'),
        ('Cognizant', 'Multinational IT firm.', 'Programmer Analyst', '4.0 LPA', 6.5, 'CSE,IT,ECE,EEE', '2024-06-30', 'Chennai'),
        ('Amazon', 'Global e-commerce and cloud leader.', 'SDE-1', '18 LPA', 8.0, 'CSE,IT', '2024-07-15', 'Hyderabad'),
        ('Google', 'World\'s leading search and technology company.', 'Software Engineer', '25 LPA', 8.5, 'CSE,IT', '2024-08-01', 'Bangalore'),
        ('Microsoft', 'Global software and cloud company.', 'Software Engineer', '20 LPA', 8.0, 'CSE,IT', '2024-07-20', 'Hyderabad'),
    ]
    c.executemany('''INSERT OR IGNORE INTO companies (name, description, role, package, eligibility_cgpa, branches, last_date, location)
                     VALUES (?,?,?,?,?,?,?,?)''', sample)

    conn.commit()
    conn.close()

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def student_logged_in():
    return 'student_id' in session

def admin_logged_in():
    return 'admin_id' in session

# ─────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────
@app.route('/')
def home():
    conn = get_db()
    companies = conn.execute('SELECT * FROM companies ORDER BY added_at DESC LIMIT 6').fetchall()
    total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_companies = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    total_placed = conn.execute("SELECT COUNT(DISTINCT student_id) FROM applications WHERE status='Selected'").fetchone()[0]
    conn.close()
    return render_template('home.html', companies=companies,
                           total_students=total_students,
                           total_companies=total_companies,
                           total_placed=total_placed)

# ─────────────────────────────────────────
#  STUDENT REGISTER / LOGIN / LOGOUT
# ─────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = hash_password(request.form['password'])
        phone = request.form['phone'].strip()
        branch = request.form['branch'].strip()
        cgpa = float(request.form['cgpa'])
        skills = request.form['skills'].strip()
        resume_link = request.form['resume_link'].strip()

        conn = get_db()
        try:
            conn.execute('''INSERT INTO students (name,email,password,phone,branch,cgpa,skills,resume_link)
                            VALUES (?,?,?,?,?,?,?,?)''',
                         (name, email, password, phone, branch, cgpa, skills, resume_link))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('student_login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = hash_password(request.form['password'])
        conn = get_db()
        student = conn.execute('SELECT * FROM students WHERE email=? AND password=?', (email, password)).fetchone()
        conn.close()
        if student:
            session['student_id'] = student['id']
            session['student_name'] = student['name']
            flash(f'Welcome back, {student["name"]}!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('student_login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

# ─────────────────────────────────────────
#  STUDENT DASHBOARD
# ─────────────────────────────────────────
@app.route('/dashboard')
def student_dashboard():
    if not student_logged_in():
        return redirect(url_for('student_login'))
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id=?', (session['student_id'],)).fetchone()
    applications = conn.execute('''
        SELECT a.*, c.name as company_name, c.role, c.package, c.location
        FROM applications a JOIN companies c ON a.company_id = c.id
        WHERE a.student_id = ?
        ORDER BY a.applied_at DESC
    ''', (session['student_id'],)).fetchall()
    conn.close()
    return render_template('student_dashboard.html', student=student, applications=applications)

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if not student_logged_in():
        return redirect(url_for('student_login'))
    
    conn = get_db()
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        branch = request.form['branch'].strip()
        cgpa = float(request.form['cgpa'])
        skills = request.form['skills'].strip()
        resume_link = request.form['resume_link'].strip()
        
        # Ek single line mein query likh di taaki indentation ka jhanjhat hi khatam ho jaye
        query = "UPDATE students SET name=?, phone=?, branch=?, cgpa=?, skills=?, resume_link=? WHERE id=?"
        params = (name, phone, branch, cgpa, skills, resume_link, session['student_id'])
        conn.execute(query, params)
        
        conn.commit()
        session['student_name'] = name
        flash('Profile updated!', 'success')
        conn.close()
        return redirect(url_for('student_dashboard'))
    
    student = conn.execute('SELECT * FROM students WHERE id=?', (session['student_id'],)).fetchone()
    conn.close()
    return render_template('edit_profile.html', student=student)

# ─────────────────────────────────────────
#  COMPANIES LIST (Public)
# ─────────────────────────────────────────
@app.route('/companies')
def companies():
    conn = get_db()
    companies = conn.execute('SELECT * FROM companies ORDER BY added_at DESC').fetchall()
    applied_ids = []
    if student_logged_in():
        rows = conn.execute('SELECT company_id FROM applications WHERE student_id=?', (session['student_id'],)).fetchall()
        applied_ids = [r['company_id'] for r in rows]
    conn.close()
    return render_template('companies.html', companies=companies, applied_ids=applied_ids)

@app.route('/apply/<int:company_id>')
def apply(company_id):
    if not student_logged_in():
        flash('Please login to apply.', 'warning')
        return redirect(url_for('student_login'))
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id=?', (session['student_id'],)).fetchone()
    company = conn.execute('SELECT * FROM companies WHERE id=?', (company_id,)).fetchone()
    if not company:
        flash('Company not found!', 'danger')
        conn.close()
        return redirect(url_for('companies'))
    if student['cgpa'] < company['eligibility_cgpa']:
        flash(f'You need CGPA ≥ {company["eligibility_cgpa"]} to apply for {company["name"]}.', 'danger')
        conn.close()
        return redirect(url_for('companies'))
    try:
        conn.execute('INSERT INTO applications (student_id, company_id) VALUES (?,?)',
                     (session['student_id'], company_id))
        conn.commit()
        flash(f'Successfully applied to {company["name"]}!', 'success')
    except sqlite3.IntegrityError:
        flash('You have already applied to this company.', 'warning')
    finally:
        conn.close()
    return redirect(url_for('companies'))

# ─────────────────────────────────────────
#  ADMIN LOGIN / LOGOUT
# ─────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = hash_password(request.form['password'])
        conn = get_db()
        admin = conn.execute('SELECT * FROM admins WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()
        if admin:
            session['admin_id'] = admin['id']
            session['admin_name'] = admin['username']
            flash('Admin logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials!', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('home'))

# ─────────────────────────────────────────
#  ADMIN DASHBOARD
# ─────────────────────────────────────────
@app.route('/admin')
def admin_dashboard():
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    total_companies = conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0]
    total_applications = conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0]
    total_placed = conn.execute("SELECT COUNT(DISTINCT student_id) FROM applications WHERE status='Selected'").fetchone()[0]
    recent_apps = conn.execute('''
        SELECT a.*, s.name as student_name, s.branch, s.cgpa, c.name as company_name
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN companies c ON a.company_id = c.id
        ORDER BY a.applied_at DESC LIMIT 10
    ''').fetchall()
    conn.close()
    return render_template('admin_dashboard.html',
                           total_students=total_students,
                           total_companies=total_companies,
                           total_applications=total_applications,
                           total_placed=total_placed,
                           recent_apps=recent_apps)

@app.route('/admin/students')
def admin_students():
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    students = conn.execute('SELECT * FROM students ORDER BY registered_at DESC').fetchall()
    conn.close()
    return render_template('admin_students.html', students=students)

@app.route('/admin/students/delete/<int:sid>')
def delete_student(sid):
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    conn.execute('DELETE FROM applications WHERE student_id=?', (sid,))
    conn.execute('DELETE FROM students WHERE id=?', (sid,))
    conn.commit()
    conn.close()
    flash('Student deleted.', 'info')
    return redirect(url_for('admin_students'))

@app.route('/admin/companies')
def admin_companies():
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    companies = conn.execute('SELECT * FROM companies ORDER BY added_at DESC').fetchall()
    conn.close()
    return render_template('admin_companies.html', companies=companies)

@app.route('/admin/companies/add', methods=['GET', 'POST'])
def add_company():
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        conn = get_db()
        conn.execute('''INSERT INTO companies (name,description,role,package,eligibility_cgpa,branches,last_date,location)
                        VALUES (?,?,?,?,?,?,?,?)''',
                     (request.form['name'], request.form['description'], request.form['role'],
                      request.form['package'], float(request.form['eligibility_cgpa']),
                      request.form['branches'], request.form['last_date'], request.form['location']))
        conn.commit()
        conn.close()
        flash('Company added successfully!', 'success')
        return redirect(url_for('admin_companies'))
    return render_template('add_company.html')

@app.route('/admin/companies/edit/<int:cid>', methods=['GET', 'POST'])
def edit_company(cid):
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    company = conn.execute('SELECT * FROM companies WHERE id=?', (cid,)).fetchone()
    if request.method == 'POST':
        conn.execute('''UPDATE companies SET name=?,description=?,role=?,package=?,eligibility_cgpa=?,branches=?,last_date=?,location=? WHERE id=?''',
                     (request.form['name'], request.form['description'], request.form['role'],
                      request.form['package'], float(request.form['eligibility_cgpa']),
                      request.form['branches'], request.form['last_date'], request.form['location'], cid))
        conn.commit()
        conn.close()
        flash('Company updated!', 'success')
        return redirect(url_for('admin_companies'))
    conn.close()
    return render_template('edit_company.html', company=company)

@app.route('/admin/companies/delete/<int:cid>')
def delete_company(cid):
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    conn.execute('DELETE FROM applications WHERE company_id=?', (cid,))
    conn.execute('DELETE FROM companies WHERE id=?', (cid,))
    conn.commit()
    conn.close()
    flash('Company deleted.', 'info')
    return redirect(url_for('admin_companies'))

@app.route('/admin/applications')
def admin_applications():
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    conn = get_db()
    apps = conn.execute('''
        SELECT a.id, a.status, a.applied_at,
               s.name as student_name, s.email, s.branch, s.cgpa,
               c.name as company_name, c.role, c.package
        FROM applications a
        JOIN students s ON a.student_id = s.id
        JOIN companies c ON a.company_id = c.id
        ORDER BY a.applied_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_applications.html', apps=apps)

@app.route('/admin/applications/status/<int:app_id>/<status>')
def update_status(app_id, status):
    if not admin_logged_in():
        return redirect(url_for('admin_login'))
    allowed = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
    if status in allowed:
        conn = get_db()
        conn.execute('UPDATE applications SET status=? WHERE id=?', (status, app_id))
        conn.commit()
        conn.close()
        flash(f'Status updated to "{status}".', 'success')
    return redirect(url_for('admin_applications'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
