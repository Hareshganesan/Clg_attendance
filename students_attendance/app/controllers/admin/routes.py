# app/controllers/admin/routes.py
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.controllers.admin import admin
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course, Enrollment
from app.models.attendance import Attendance, AttendanceSession
from app.controllers.admin.forms import (
    AddFacultyForm, AddStudentForm, AddCourseForm, 
    EditUserForm, EditCourseForm
)
from app.utils.decorators import admin_required
import pandas as pd
import plotly.express as px
import plotly.utils
import json

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get some statistics for the dashboard
    total_students = Student.query.count()
    total_faculty = Faculty.query.count()
    total_courses = Course.query.count()
    total_sessions = AttendanceSession.query.count()
    
    # Get recent attendance sessions
    recent_sessions = AttendanceSession.query.order_by(AttendanceSession.date.desc()).limit(5).all()
    
    # Get attendance by department
    attendance_by_dept = db.session.query(
        Student.department,
        db.func.count(Attendance.id).label('count'),
        db.func.count(Attendance.id).filter(Attendance.status == 'present').label('present_count')
    ).join(
        Attendance, Attendance.student_id == Student.id
    ).group_by(
        Student.department
    ).all()
    
    dept_data = {
        'departments': [d[0] for d in attendance_by_dept],
        'attendance_rates': [round((d[2] / d[1]) * 100, 2) if d[1] > 0 else 0 for d in attendance_by_dept]
    }
    
    # Create a bar chart for attendance by department
    if dept_data['departments']:
        fig = px.bar(
            x=dept_data['departments'],
            y=dept_data['attendance_rates'],
            labels={'x': 'Department', 'y': 'Attendance Rate (%)'},
            title='Attendance Rate by Department'
        )
        dept_chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
        dept_chart_json = None
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        total_students=total_students,
        total_faculty=total_faculty,
        total_courses=total_courses,
        total_sessions=total_sessions,
        recent_sessions=recent_sessions,
        dept_chart_json=dept_chart_json
    )

@admin.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=15)
    return render_template('admin/users.html', title='Manage Users', users=users)

@admin.route('/users/<int:user_id>')
@login_required
@admin_required
def user_details(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/user_details.html', title='User Details', user=user)

@admin.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'User {user.username} has been updated!', 'success')
        return redirect(url_for('admin.user_details', user_id=user.id))
    
    # Pre-populate form with user data
    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.is_active.data = user.is_active
    
    return render_template('admin/edit_user.html', title='Edit User', form=form, user=user)

@admin.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    students = Student.query.join(User).paginate(page=page, per_page=15)
    return render_template('admin/students.html', title='Manage Students', students=students)

@admin.route('/faculty')
@login_required
@admin_required
def faculty():
    page = request.args.get('page', 1, type=int)
    faculty = Faculty.query.join(User).paginate(page=page, per_page=15)
    return render_template('admin/faculty.html', title='Manage Faculty', faculty=faculty)

@admin.route('/faculty/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_faculty():
    form = AddFacultyForm()
    
    if form.validate_on_submit():
        # Create a new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='faculty'
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID
        
        # Create a faculty record
        faculty = Faculty(
            user_id=user.id,
            employee_id=form.employee_id.data,
            department=form.department.data,
            designation=form.designation.data,
            joining_date=form.joining_date.data
        )
        
        db.session.add(faculty)
        db.session.commit()
        
        flash(f'Faculty member {user.first_name} {user.last_name} has been added!', 'success')
        return redirect(url_for('admin.faculty'))
    
    return render_template('admin/add_faculty.html', title='Add Faculty', form=form)

@admin.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    form = AddStudentForm()
    
    if form.validate_on_submit():
        # Create a new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='student'
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.flush()  # Flush to get the user ID
        
        # Create a student record
        student = Student(
            user_id=user.id,
            roll_number=form.roll_number.data,
            enrollment_year=form.enrollment_year.data,
            department=form.department.data,
            semester=form.semester.data,
            section=form.section.data
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash(f'Student {user.first_name} {user.last_name} has been added!', 'success')
        return redirect(url_for('admin.students'))
    
    return render_template('admin/add_student.html', title='Add Student', form=form)

@admin.route('/courses')
@login_required
@admin_required
def courses():
    page = request.args.get('page', 1, type=int)
    courses = Course.query.paginate(page=page, per_page=15)
    return render_template('admin/courses.html', title='Manage Courses', courses=courses)

@admin.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    form = AddCourseForm()
    
    # Get all faculty members for the dropdown
    faculty_members = Faculty.query.join(User).filter(User.is_active == True).all()
    form.faculty_id.choices = [(f.id, f"{f.user.first_name} {f.user.last_name} - {f.department}") for f in faculty_members]
    
    if form.validate_on_submit():
        course = Course(
            course_code=form.course_code.data,
            title=form.title.data,
            description=form.description.data,
            credits=form.credits.data,
            faculty_id=form.faculty_id.data,
            department=form.department.data,
            semester=form.semester.data,
            year=form.year.data,
            is_active=form.is_active.data
        )
        
        db.session.add(course)
        db.session.commit()
        
        flash(f'Course {course.title} has been added!', 'success')
        return redirect(url_for('admin.courses'))
    
    return render_template('admin/add_course.html', title='Add Course', form=form)

@admin.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)
    form = EditCourseForm()
    
    # Get all faculty members for the dropdown
    faculty_members = Faculty.query.join(User).filter(User.is_active == True).all()
    form.faculty_id.choices = [(f.id, f"{f.user.first_name} {f.user.last_name} - {f.department}") for f in faculty_members]
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.credits = form.credits.data
        course.faculty_id = form.faculty_id.data
        course.department = form.department.data
        course.semester = form.semester.data
        course.year = form.year.data
        course.is_active = form.is_active.data
        
        db.session.commit()
        flash(f'Course {course.title} has been updated!', 'success')
        return redirect(url_for('admin.courses'))
    
    # Pre-populate form with course data
    if request.method == 'GET':
        form.title.data = course.title
        form.description.data = course.description
        form.credits.data = course.credits
        form.faculty_id.data = course.faculty_id
        form.department.data = course.department
        form.semester.data = course.semester
        form.year.data = course.year
        form.is_active.data = course.is_active
    
    return render_template('admin/edit_course.html', title='Edit Course', form=form, course=course)

@admin.route('/attendance')
@login_required
@admin_required
def attendance():
    page = request.args.get('page', 1, type=int)
    
    # Get attendance sessions with course and faculty info
    sessions = AttendanceSession.query.join(
        Course, AttendanceSession.course_id == Course.id
    ).join(
        Faculty, AttendanceSession.faculty_id == Faculty.id
    ).join(
        User, Faculty.user_id == User.id
    ).add_columns(
        AttendanceSession.id,
        AttendanceSession.date,
        AttendanceSession.start_time,
        AttendanceSession.end_time,
        Course.course_code,
        Course.title.label('course_title'),
        User.first_name.label('faculty_first_name'),
        User.last_name.label('faculty_last_name')
    ).order_by(AttendanceSession.date.desc()).paginate(page=page, per_page=15)
    
    return render_template('admin/attendance.html', title='Attendance Records', sessions=sessions)

@admin.route('/attendance/session/<int:session_id>')
@login_required
@admin_required
def attendance_session(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    
    # Get all enrolled students for this course
    enrolled_students = Student.query.join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(
        Enrollment.course_id == session.course_id,
        Enrollment.is_active == True
    ).all()
    
    # Get attendance records for this session
    attendance_records = Attendance.query.filter_by(session_id=session_id).all()
    
    # Create a dictionary for easier lookup
    attendance_dict = {a.student_id: a for a in attendance_records}
    
    # Prepare student attendance data
    students_attendance = []
    for student in enrolled_students:
        attendance_record = attendance_dict.get(student.id)
        status = attendance_record.status if attendance_record else 'absent'
        timestamp = attendance_record.timestamp if attendance_record else None
        
        students_attendance.append({
            'student_id': student.id,
            'roll_number': student.roll_number,
            'name': f"{student.user.first_name} {student.user.last_name}",
            'status': status,
            'timestamp': timestamp
        })
    
    return render_template(
        'admin/attendance_session.html',
        title=f'Attendance for {session.course.title} on {session.date}',
        session=session,
        students_attendance=students_attendance
    )

@admin.route('/reports')
@login_required
@admin_required
def reports():
    # Get all departments for filtering
    departments = Student.query.with_entities(Student.department).distinct().all()
    departments = [d[0] for d in departments]
    
    # Get all courses for filtering
    courses = Course.query.all()
    
    return render_template(
        'admin/reports.html',
        title='Reports',
        departments=departments,
        courses=courses
    )

@admin.route('/api/reports/attendance_by_department', methods=['GET'])
@login_required
@admin_required
def api_attendance_by_department():
    # Get attendance data by department
    attendance_by_dept = db.session.query(
        Student.department,
        db.func.count(Attendance.id).label('count'),
        db.func.count(Attendance.id).filter(Attendance.status == 'present').label('present_count')
    ).join(
        Attendance, Attendance.student_id == Student.id
    ).group_by(
        Student.department
    ).all()
    
    data = []
    for dept, total, present in attendance_by_dept:
        attendance_rate = round((present / total) * 100, 2) if total > 0 else 0
        data.append({
            'department': dept,
            'total_records': total,
            'present_records': present,
            'attendance_rate': attendance_rate
        })
    
    return jsonify(data)

@admin.route('/api/reports/attendance_by_course', methods=['GET'])
@login_required
@admin_required
def api_attendance_by_course():
    # Get attendance data by course
    attendance_by_course = db.session.query(
        Course.id,
        Course.course_code,
        Course.title,
        db.func.count(Attendance.id).label('count'),
        db.func.count(Attendance.id).filter(Attendance.status == 'present').label('present_count')
    ).join(
        AttendanceSession, AttendanceSession.course_id == Course.id
    ).join(
        Attendance, Attendance.session_id == AttendanceSession.id
    ).group_by(
        Course.id, Course.course_code, Course.title
    ).all()
    
    data = []
    for id, code, title, total, present in attendance_by_course:
        attendance_rate = round((present / total) * 100, 2) if total > 0 else 0
        data.append({
            'course_id': id,
            'course_code': code,
            'course_title': title,
            'total_records': total,
            'present_records': present,
            'attendance_rate': attendance_rate
        })
    
    return jsonify(data)

@admin.route('/bulk_upload_students', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_upload_students():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
            
        if file and file.filename.endswith('.csv'):
            try:
                # Read the CSV file
                df = pd.read_csv(file)
                
                # Define required columns
                required_columns = [
                    'first_name', 'last_name', 'email', 'username', 
                    'roll_number', 'enrollment_year', 'department', 
                    'semester', 'section'
                ]
                
                # Check if all required columns are present
                for col in required_columns:
                    if col not in df.columns:
                        flash(f'Missing required column: {col}', 'danger')
                        return redirect(request.url)
                
                # Process each row
                success_count = 0
                error_count = 0
                errors = []
                
                for _, row in df.iterrows():
                    try:
                        # Check if user with this email or username already exists
                        if User.query.filter_by(email=row['email']).first() or User.query.filter_by(username=row['username']).first():
                            errors.append(f"User with email {row['email']} or username {row['username']} already exists")
                            error_count += 1
                            continue
                            
                        # Check if student with this roll number already exists
                        if Student.query.filter_by(roll_number=row['roll_number']).first():
                            errors.append(f"Student with roll number {row['roll_number']} already exists")
                            error_count += 1
                            continue
                        
                        # Create user
                        user = User(
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            email=row['email'],
                            username=row['username'],
                            role='student'
                        )
                        
                        # Generate a default password (e.g., roll number)
                        user.set_password(str(row['roll_number']))
                        
                        db.session.add(user)
                        db.session.flush()  # Get the user ID
                        
                        # Create student
                        student = Student(
                            user_id=user.id,
                            roll_number=row['roll_number'],
                            enrollment_year=int(row['enrollment_year']),
                            department=row['department'],
                            semester=int(row['semester']),
                            section=row['section']
                        )
                        
                        db.session.add(student)
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f"Error processing row {_+2}: {str(e)}")
                        error_count += 1
                
                db.session.commit()
                
                flash(f'Successfully added {success_count} students. {error_count} errors.', 'info')
                if errors:
                    for error in errors[:10]:  # Show only first 10 errors
                        flash(error, 'warning')
                    if len(errors) > 10:
                        flash(f'... and {len(errors) - 10} more errors', 'warning')
                
                return redirect(url_for('admin.students'))
                
            except Exception as e:
                flash(f'Error processing CSV file: {str(e)}', 'danger')
                return redirect(request.url)
        else:
            flash('Only CSV files are allowed', 'danger')
            return redirect(request.url)
    
    return render_template('admin/bulk_upload_students.html', title='Bulk Upload Students')
