# app/models/course.py
from datetime import datetime
from app import db

class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    faculty = db.relationship('Faculty', back_populates='courses')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade='all, delete-orphan')
    attendance_sessions = db.relationship('AttendanceSession', back_populates='course', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.course_code}>'
    
    def get_enrolled_students(self):
        """Get all students enrolled in this course"""
        from app.models.student import Student
        
        enrolled_students = Student.query.join(Enrollment).filter(
            Enrollment.course_id == self.id
        ).all()
        
        return enrolled_students
    
    def get_attendance_stats(self):
        """Get attendance statistics for this course"""
        from app.models.attendance import AttendanceSession, Attendance
        from sqlalchemy import func
        
        # Get all enrolled students
        enrolled_students = self.get_enrolled_students()
        total_students = len(enrolled_students)
        
        # Get all attendance sessions for this course
        sessions = AttendanceSession.query.filter_by(course_id=self.id).all()
        total_sessions = len(sessions)
        
        # Initialize statistics
        stats = {
            'total_sessions': total_sessions,
            'total_students': total_students,
            'average_attendance_percentage': 0,
            'student_stats': []
        }
        
        if total_sessions == 0 or total_students == 0:
            return stats
        
        # Calculate per-student attendance
        for student in enrolled_students:
            present_count = Attendance.query.join(AttendanceSession).filter(
                Attendance.student_id == student.id,
                AttendanceSession.course_id == self.id,
                Attendance.status == 'present'
            ).count()
            
            attendance_percentage = (present_count / total_sessions) * 100 if total_sessions > 0 else 0
            
            stats['student_stats'].append({
                'student_id': student.id,
                'name': student.user.get_full_name(),
                'roll_number': student.roll_number,
                'present_count': present_count,
                'absent_count': total_sessions - present_count,
                'attendance_percentage': attendance_percentage
            })
        
        # Calculate average attendance percentage
        if stats['student_stats']:
            avg_percentage = sum(s['attendance_percentage'] for s in stats['student_stats']) / len(stats['student_stats'])
            stats['average_attendance_percentage'] = avg_percentage
        
        return stats


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),
    )
    
    def __repr__(self):
        return f'<Enrollment {self.student_id} in {self.course_id}>'
