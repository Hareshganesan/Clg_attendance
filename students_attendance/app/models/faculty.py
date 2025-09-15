# app/models/faculty.py
from app import db
from app.models.user import User

class Faculty(db.Model):
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('faculty', uselist=False, cascade='all, delete-orphan'))
    courses = db.relationship('Course', back_populates='faculty', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Faculty {self.employee_id}>'
    
    def get_active_courses(self):
        """Get all active courses taught by this faculty member"""
        from app.models.course import Course
        return Course.query.filter_by(faculty_id=self.id, is_active=True).all()
    
    def get_course_attendance_stats(self, course_id):
        """Get attendance statistics for a specific course"""
        from app.models.attendance import AttendanceSession
        from app.models.course import Enrollment
        from sqlalchemy import func
        
        # Get total number of students enrolled in the course
        total_students = Enrollment.query.filter_by(course_id=course_id).count()
        
        # Get all attendance sessions for this course
        sessions = AttendanceSession.query.filter_by(
            course_id=course_id, 
            faculty_id=self.id
        ).all()
        
        # Calculate statistics
        stats = {
            'total_sessions': len(sessions),
            'total_students': total_students,
            'session_details': []
        }
        
        for session in sessions:
            present_count = session.attendances.filter_by(status='present').count()
            absent_count = total_students - present_count
            
            stats['session_details'].append({
                'date': session.date,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'present_count': present_count,
                'absent_count': absent_count,
                'attendance_percentage': (present_count / total_students) * 100 if total_students > 0 else 0
            })
        
        return stats
