# app/models/student.py
from app import db
from app.models.user import User

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    enrollment_year = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    section = db.Column(db.String(10))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('student', uselist=False, cascade='all, delete-orphan'))
    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', back_populates='student', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.roll_number}>'
    
    def get_attendance_percentage(self, course_id=None):
        from app.models.attendance import Attendance, AttendanceSession
        
        if course_id:
            # Get attendance for a specific course
            total_sessions = AttendanceSession.query.filter_by(course_id=course_id).count()
            if total_sessions == 0:
                return 0
                
            attended_sessions = Attendance.query.join(AttendanceSession).filter(
                Attendance.student_id == self.id,
                AttendanceSession.course_id == course_id,
                Attendance.status == 'present'
            ).count()
            
            return (attended_sessions / total_sessions) * 100
        else:
            # Get overall attendance across all courses
            # This requires determining which courses the student is enrolled in
            from app.models.course import Enrollment
            
            enrollments = Enrollment.query.filter_by(student_id=self.id).all()
            if not enrollments:
                return 0
                
            course_ids = [enrollment.course_id for enrollment in enrollments]
            
            total_sessions = AttendanceSession.query.filter(
                AttendanceSession.course_id.in_(course_ids)
            ).count()
            
            if total_sessions == 0:
                return 0
                
            attended_sessions = Attendance.query.join(AttendanceSession).filter(
                Attendance.student_id == self.id,
                AttendanceSession.course_id.in_(course_ids),
                Attendance.status == 'present'
            ).count()
            
            return (attended_sessions / total_sessions) * 100
