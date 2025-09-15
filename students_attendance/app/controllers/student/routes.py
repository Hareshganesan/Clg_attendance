# app/controllers/student/routes.py
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.controllers.student import student
from app.models.user import User
from app.models.student import Student
from app.models.course import Course, Enrollment
from app.models.attendance import Attendance, AttendanceSession
from app.utils.decorators import student_required
from datetime import datetime
import json

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    # Get student details
    student_user = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get active enrollments
    enrollments = Enrollment.query.filter_by(
        student_id=student_user.id,
        is_active=True
    ).join(Course).filter(Course.is_active == True).all()
    
    # Get attendance percentage for each course
    course_attendance = []
    for enrollment in enrollments:
        course = enrollment.course
        
        # Get attendance percentage for this course
        attendance_percentage = student_user.get_attendance_percentage(course.id)
        
        course_attendance.append({
            'course': course,
            'attendance_percentage': attendance_percentage
        })
    
    # Get overall attendance percentage
    overall_percentage = student_user.get_attendance_percentage()
    
    # Get recent attendance records
    recent_attendance = Attendance.query.filter_by(
        student_id=student_user.id
    ).join(
        AttendanceSession
    ).order_by(Attendance.timestamp.desc()).limit(5).all()
    
    return render_template(
        'student/dashboard.html',
        title='Student Dashboard',
        student=student_user,
        course_attendance=course_attendance,
        overall_percentage=overall_percentage,
        recent_attendance=recent_attendance
    )

@student.route('/courses')
@login_required
@student_required
def courses():
    # Get student details
    student_user = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get all enrollments
    enrollments = Enrollment.query.filter_by(
        student_id=student_user.id
    ).join(Course).all()
    
    return render_template(
        'student/courses.html',
        title='My Courses',
        enrollments=enrollments
    )

@student.route('/course/<int:course_id>')
@login_required
@student_required
def course_details(course_id):
    # Get student details
    student_user = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Check if student is enrolled in this course
    enrollment = Enrollment.query.filter_by(
        student_id=student_user.id,
        course_id=course_id
    ).first_or_404()
    
    # Get course details
    course = enrollment.course
    
    # Get attendance records for this course
    attendance_records = Attendance.query.join(
        AttendanceSession
    ).filter(
        Attendance.student_id == student_user.id,
        AttendanceSession.course_id == course_id
    ).all()
    
    # Get all attendance sessions for this course
    sessions = AttendanceSession.query.filter_by(
        course_id=course_id
    ).order_by(AttendanceSession.date.desc()).all()
    
    # Create a dictionary for easier lookup
    attendance_dict = {a.session_id: a for a in attendance_records}
    
    # Prepare session attendance data
    sessions_attendance = []
    for session in sessions:
        attendance = attendance_dict.get(session.id)
        status = attendance.status if attendance else 'absent'
        
        sessions_attendance.append({
            'session': session,
            'status': status,
            'timestamp': attendance.timestamp if attendance else None
        })
    
    # Calculate attendance percentage for this course
    attendance_percentage = student_user.get_attendance_percentage(course_id)
    
    return render_template(
        'student/course_details.html',
        title=f'Course: {course.title}',
        course=course,
        sessions_attendance=sessions_attendance,
        attendance_percentage=attendance_percentage
    )

@student.route('/attendance')
@login_required
@student_required
def attendance():
    # Get student details
    student_user = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get all attendance records
    attendance_records = Attendance.query.filter_by(
        student_id=student_user.id
    ).join(
        AttendanceSession
    ).order_by(AttendanceSession.date.desc()).all()
    
    # Group attendance records by course
    courses_attendance = {}
    for attendance in attendance_records:
        session = attendance.session
        course_id = session.course_id
        
        if course_id not in courses_attendance:
            courses_attendance[course_id] = {
                'course': session.course,
                'sessions': []
            }
        
        courses_attendance[course_id]['sessions'].append({
            'session': session,
            'status': attendance.status,
            'timestamp': attendance.timestamp
        })
    
    return render_template(
        'student/attendance.html',
        title='My Attendance',
        courses_attendance=courses_attendance
    )

@student.route('/mark_attendance', methods=['GET', 'POST'])
@login_required
@student_required
def mark_attendance():
    # Get student details
    student_user = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        session_code = request.form.get('session_code')
        
        if not session_code:
            flash('Please enter a session code.', 'danger')
            return redirect(url_for('student.mark_attendance'))
        
        # Find the attendance session with this code
        session = AttendanceSession.query.filter_by(
            session_code=session_code,
            is_active=True
        ).first()
        
        if not session:
            flash('Invalid session code or session is not active.', 'danger')
            return redirect(url_for('student.mark_attendance'))
        
        # Check if student is enrolled in this course
        enrollment = Enrollment.query.filter_by(
            student_id=student_user.id,
            course_id=session.course_id,
            is_active=True
        ).first()
        
        if not enrollment:
            flash('You are not enrolled in this course.', 'danger')
            return redirect(url_for('student.mark_attendance'))
        
        # Check if attendance already marked
        existing_attendance = Attendance.query.filter_by(
            session_id=session.id,
            student_id=student_user.id
        ).first()
        
        if existing_attendance:
            flash('Your attendance has already been marked for this session.', 'info')
            return redirect(url_for('student.course_details', course_id=session.course_id))
        
        # Mark attendance
        attendance = Attendance(
            session_id=session.id,
            student_id=student_user.id,
            status='present',
            ip_address=request.remote_addr,
            device_info=request.user_agent.string
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        flash('Your attendance has been marked successfully!', 'success')
        return redirect(url_for('student.course_details', course_id=session.course_id))
    
    return render_template(
        'student/mark_attendance.html',
        title='Mark Attendance'
    )

@student.route('/scan_qr', methods=['GET'])
@login_required
@student_required
def scan_qr():
    return render_template(
        'student/scan_qr.html',
        title='Scan QR Code'
    )

@student.route('/api/mark_attendance', methods=['POST'])
@login_required
@student_required
def api_mark_attendance():
    # Get student details
    student_user = Student.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Get session code from request
    data = request.json
    session_code = data.get('session_code')
    
    if not session_code:
        return jsonify({'success': False, 'message': 'Session code is required.'}), 400
    
    # Find the attendance session with this code
    session = AttendanceSession.query.filter_by(
        session_code=session_code,
        is_active=True
    ).first()
    
    if not session:
        return jsonify({'success': False, 'message': 'Invalid session code or session is not active.'}), 400
    
    # Check if student is enrolled in this course
    enrollment = Enrollment.query.filter_by(
        student_id=student_user.id,
        course_id=session.course_id,
        is_active=True
    ).first()
    
    if not enrollment:
        return jsonify({'success': False, 'message': 'You are not enrolled in this course.'}), 400
    
    # Check if attendance already marked
    existing_attendance = Attendance.query.filter_by(
        session_id=session.id,
        student_id=student_user.id
    ).first()
    
    if existing_attendance:
        return jsonify({'success': False, 'message': 'Your attendance has already been marked for this session.'}), 400
    
    # Mark attendance
    attendance = Attendance(
        session_id=session.id,
        student_id=student_user.id,
        status='present',
        ip_address=request.remote_addr,
        device_info=request.user_agent.string
    )
    
    db.session.add(attendance)
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Your attendance has been marked successfully!',
        'course': {
            'id': session.course.id,
            'title': session.course.title
        }
    })
