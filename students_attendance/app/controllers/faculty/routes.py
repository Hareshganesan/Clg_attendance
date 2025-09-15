# app/controllers/faculty/routes.py
from flask import render_template, url_for, flash, redirect, request, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.controllers.faculty import faculty
from app.models.user import User
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.course import Course, Enrollment
from app.models.attendance import Attendance, AttendanceSession
from app.controllers.faculty.forms import CreateAttendanceSessionForm, MarkAttendanceForm
from app.utils.decorators import faculty_required
from app.utils.qrcode_generator import generate_session_code, generate_qr_code
from datetime import datetime, date, time
import json

@faculty.route('/dashboard')
@login_required
@faculty_required
def dashboard():
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get active courses taught by this faculty
    active_courses = Course.query.filter_by(faculty_id=faculty_user.id, is_active=True).all()
    
    # Get recent attendance sessions
    recent_sessions = AttendanceSession.query.filter_by(
        faculty_id=faculty_user.id
    ).order_by(AttendanceSession.date.desc()).limit(5).all()
    
    # Get course attendance stats
    course_stats = []
    for course in active_courses:
        stats = faculty_user.get_course_attendance_stats(course.id)
        
        # Calculate overall attendance percentage
        if stats['total_sessions'] > 0 and stats['total_students'] > 0:
            # Get total present attendance records
            present_count = 0
            for session in stats['session_details']:
                present_count += session['present_count']
                
            # Total possible attendance records
            total_possible = stats['total_sessions'] * stats['total_students']
            
            # Overall attendance rate
            overall_rate = (present_count / total_possible) * 100 if total_possible > 0 else 0
        else:
            overall_rate = 0
            
        course_stats.append({
            'course': course,
            'total_sessions': stats['total_sessions'],
            'total_students': stats['total_students'],
            'overall_attendance_rate': overall_rate
        })
    
    return render_template(
        'faculty/dashboard.html',
        title='Faculty Dashboard',
        faculty=faculty_user,
        active_courses=active_courses,
        recent_sessions=recent_sessions,
        course_stats=course_stats
    )

@faculty.route('/courses')
@login_required
@faculty_required
def courses():
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get all courses taught by this faculty
    courses = Course.query.filter_by(faculty_id=faculty_user.id).all()
    
    return render_template(
        'faculty/courses.html',
        title='My Courses',
        courses=courses
    )

@faculty.route('/course/<int:course_id>')
@login_required
@faculty_required
def course_details(course_id):
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get course details
    course = Course.query.filter_by(id=course_id, faculty_id=faculty_user.id).first_or_404()
    
    # Get enrolled students
    enrolled_students = Student.query.join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(
        Enrollment.course_id == course_id,
        Enrollment.is_active == True
    ).join(
        User, Student.user_id == User.id
    ).add_columns(
        Student.id,
        Student.roll_number,
        User.first_name,
        User.last_name
    ).all()
    
    # Get attendance sessions for this course
    attendance_sessions = AttendanceSession.query.filter_by(
        course_id=course_id,
        faculty_id=faculty_user.id
    ).order_by(AttendanceSession.date.desc()).all()
    
    # Get attendance statistics
    course_stats = course.get_attendance_stats()
    
    return render_template(
        'faculty/course_details.html',
        title=f'Course: {course.title}',
        course=course,
        enrolled_students=enrolled_students,
        attendance_sessions=attendance_sessions,
        course_stats=course_stats
    )

@faculty.route('/attendance/create', methods=['GET', 'POST'])
@login_required
@faculty_required
def create_attendance():
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    form = CreateAttendanceSessionForm()
    
    # Get all courses taught by this faculty for the dropdown
    courses = Course.query.filter_by(faculty_id=faculty_user.id, is_active=True).all()
    form.course_id.choices = [(c.id, f"{c.course_code} - {c.title}") for c in courses]
    
    if form.validate_on_submit():
        # Generate a unique session code
        session_code = generate_session_code()
        
        # Create attendance session
        attendance_session = AttendanceSession(
            course_id=form.course_id.data,
            faculty_id=faculty_user.id,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            session_code=session_code,
            location=form.location.data,
            notes=form.notes.data
        )
        
        db.session.add(attendance_session)
        db.session.commit()
        
        flash('Attendance session created successfully!', 'success')
        return redirect(url_for('faculty.attendance_session', session_id=attendance_session.id))
    
    # Set default date to today
    if request.method == 'GET':
        form.date.data = date.today()
    
    return render_template(
        'faculty/create_attendance.html',
        title='Create Attendance Session',
        form=form
    )

@faculty.route('/attendance/session/<int:session_id>')
@login_required
@faculty_required
def attendance_session(session_id):
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get attendance session details
    session = AttendanceSession.query.filter_by(
        id=session_id,
        faculty_id=faculty_user.id
    ).first_or_404()
    
    # Generate QR code for the session
    qr_code = session.generate_qr_code()
    
    # Get all enrolled students for this course
    enrolled_students = Student.query.join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(
        Enrollment.course_id == session.course_id,
        Enrollment.is_active == True
    ).join(
        User, Student.user_id == User.id
    ).add_columns(
        Student.id,
        Student.roll_number,
        User.first_name,
        User.last_name
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
            'name': f"{student.first_name} {student.last_name}",
            'status': status,
            'timestamp': timestamp
        })
    
    return render_template(
        'faculty/attendance_session.html',
        title=f'Attendance for {session.course.title} on {session.date}',
        session=session,
        qr_code=qr_code,
        students_attendance=students_attendance
    )

@faculty.route('/attendance/mark/<int:session_id>', methods=['GET', 'POST'])
@login_required
@faculty_required
def mark_attendance(session_id):
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get attendance session details
    session = AttendanceSession.query.filter_by(
        id=session_id,
        faculty_id=faculty_user.id
    ).first_or_404()
    
    # Get all enrolled students for this course
    enrolled_students = Student.query.join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(
        Enrollment.course_id == session.course_id,
        Enrollment.is_active == True
    ).join(
        User, Student.user_id == User.id
    ).add_columns(
        Student.id,
        Student.roll_number,
        User.first_name,
        User.last_name
    ).all()
    
    form = MarkAttendanceForm()
    
    # Handle form submission
    if form.validate_on_submit():
        # Get the attendance data from the form
        for student in enrolled_students:
            status_field = f'status_{student.id}'
            status = request.form.get(status_field, 'absent')
            
            # Check if attendance record already exists
            attendance = Attendance.query.filter_by(
                session_id=session_id,
                student_id=student.id
            ).first()
            
            if attendance:
                # Update existing record
                attendance.status = status
                attendance.marked_by = current_user.id
                attendance.timestamp = datetime.utcnow()
            else:
                # Create new attendance record
                attendance = Attendance(
                    session_id=session_id,
                    student_id=student.id,
                    status=status,
                    marked_by=current_user.id
                )
                db.session.add(attendance)
        
        db.session.commit()
        flash('Attendance marked successfully!', 'success')
        return redirect(url_for('faculty.attendance_session', session_id=session_id))
    
    # Get existing attendance records
    attendance_records = Attendance.query.filter_by(session_id=session_id).all()
    attendance_dict = {a.student_id: a for a in attendance_records}
    
    return render_template(
        'faculty/mark_attendance.html',
        title=f'Mark Attendance for {session.course.title} on {session.date}',
        session=session,
        students=enrolled_students,
        attendance_dict=attendance_dict,
        form=form
    )

@faculty.route('/attendance/history')
@login_required
@faculty_required
def attendance_history():
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get all attendance sessions created by this faculty
    page = request.args.get('page', 1, type=int)
    sessions = AttendanceSession.query.filter_by(
        faculty_id=faculty_user.id
    ).order_by(AttendanceSession.date.desc()).paginate(page=page, per_page=10)
    
    return render_template(
        'faculty/attendance_history.html',
        title='Attendance History',
        sessions=sessions
    )

@faculty.route('/students')
@login_required
@faculty_required
def students():
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get courses taught by this faculty
    courses = Course.query.filter_by(faculty_id=faculty_user.id).all()
    course_ids = [course.id for course in courses]
    
    # Get all students enrolled in these courses
    enrolled_students = Student.query.join(
        Enrollment, Student.id == Enrollment.student_id
    ).filter(
        Enrollment.course_id.in_(course_ids),
        Enrollment.is_active == True
    ).join(
        User, Student.user_id == User.id
    ).add_columns(
        Student.id,
        Student.roll_number,
        Student.department,
        Student.semester,
        User.first_name,
        User.last_name,
        User.email
    ).distinct().all()
    
    return render_template(
        'faculty/students.html',
        title='My Students',
        students=enrolled_students,
        courses=courses
    )

@faculty.route('/student/<int:student_id>')
@login_required
@faculty_required
def student_details(student_id):
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get student details
    student = Student.query.filter_by(id=student_id).join(User).first_or_404()
    
    # Get courses taught by this faculty that the student is enrolled in
    enrollments = Enrollment.query.filter_by(
        student_id=student_id,
        is_active=True
    ).join(
        Course, Enrollment.course_id == Course.id
    ).filter(
        Course.faculty_id == faculty_user.id
    ).all()
    
    course_ids = [enrollment.course_id for enrollment in enrollments]
    
    # Get attendance statistics for each course
    attendance_stats = []
    for course_id in course_ids:
        course = Course.query.get(course_id)
        
        # Get total sessions for this course
        total_sessions = AttendanceSession.query.filter_by(
            course_id=course_id,
            faculty_id=faculty_user.id
        ).count()
        
        # Get attended sessions
        attended_sessions = Attendance.query.join(
            AttendanceSession, Attendance.session_id == AttendanceSession.id
        ).filter(
            Attendance.student_id == student_id,
            AttendanceSession.course_id == course_id,
            AttendanceSession.faculty_id == faculty_user.id,
            Attendance.status == 'present'
        ).count()
        
        # Calculate attendance percentage
        attendance_percentage = (attended_sessions / total_sessions) * 100 if total_sessions > 0 else 0
        
        attendance_stats.append({
            'course': course,
            'total_sessions': total_sessions,
            'attended_sessions': attended_sessions,
            'attendance_percentage': attendance_percentage
        })
    
    return render_template(
        'faculty/student_details.html',
        title=f'Student: {student.user.first_name} {student.user.last_name}',
        student=student,
        attendance_stats=attendance_stats
    )

@faculty.route('/reports')
@login_required
@faculty_required
def reports():
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get active courses taught by this faculty
    active_courses = Course.query.filter_by(faculty_id=faculty_user.id, is_active=True).all()
    
    return render_template(
        'faculty/reports.html',
        title='Reports',
        active_courses=active_courses
    )

@faculty.route('/api/course_attendance/<int:course_id>')
@login_required
@faculty_required
def api_course_attendance(course_id):
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get course details
    course = Course.query.filter_by(id=course_id, faculty_id=faculty_user.id).first_or_404()
    
    # Get attendance statistics
    stats = course.get_attendance_stats()
    
    return jsonify(stats)

@faculty.route('/api/student_attendance/<int:student_id>')
@login_required
@faculty_required
def api_student_attendance(student_id):
    # Get faculty member details
    faculty_user = Faculty.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get student details
    student = Student.query.filter_by(id=student_id).first_or_404()
    
    # Get courses taught by this faculty that the student is enrolled in
    course_enrollments = Enrollment.query.filter_by(
        student_id=student_id,
        is_active=True
    ).join(
        Course, Enrollment.course_id == Course.id
    ).filter(
        Course.faculty_id == faculty_user.id
    ).all()
    
    course_ids = [enrollment.course_id for enrollment in course_enrollments]
    
    # Get attendance data for each course
    attendance_data = []
    for course_id in course_ids:
        course = Course.query.get(course_id)
        
        # Get attendance sessions for this course
        sessions = AttendanceSession.query.filter_by(
            course_id=course_id,
            faculty_id=faculty_user.id
        ).order_by(AttendanceSession.date).all()
        
        session_data = []
        for session in sessions:
            # Check if student was present
            attendance = Attendance.query.filter_by(
                session_id=session.id,
                student_id=student_id
            ).first()
            
            status = attendance.status if attendance else 'absent'
            
            session_data.append({
                'date': session.date.strftime('%Y-%m-%d'),
                'status': status
            })
        
        attendance_data.append({
            'course_id': course.id,
            'course_code': course.course_code,
            'course_title': course.title,
            'sessions': session_data
        })
    
    return jsonify(attendance_data)
