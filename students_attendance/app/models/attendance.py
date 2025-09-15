# app/models/attendance.py
from datetime import datetime
import qrcode
import io
import base64
from app import db

class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    session_code = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Relationships
    course = db.relationship('Course', back_populates='attendance_sessions')
    faculty = db.relationship('Faculty')
    attendances = db.relationship('Attendance', back_populates='session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<AttendanceSession {self.course.course_code} {self.date}>'
    
    def generate_qr_code(self):
        """Generate a QR code for this attendance session"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.session_code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for embedding in HTML
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def get_attendance_count(self):
        """Get the count of present and absent students"""
        present_count = Attendance.query.filter_by(session_id=self.id, status='present').count()
        
        # Get total enrolled students for this course
        from app.models.course import Enrollment
        total_enrolled = Enrollment.query.filter_by(course_id=self.course_id, is_active=True).count()
        
        absent_count = total_enrolled - present_count
        
        return {
            'present': present_count,
            'absent': absent_count,
            'total': total_enrolled
        }


class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='present')  # 'present', 'absent', 'late'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who marked this attendance
    location = db.Column(db.String(100))  # For geolocation tracking (optional)
    ip_address = db.Column(db.String(50))  # For tracking from where attendance was marked
    device_info = db.Column(db.String(255))  # Device used to mark attendance
    comments = db.Column(db.Text)
    
    # Relationships
    session = db.relationship('AttendanceSession', back_populates='attendances')
    student = db.relationship('Student', back_populates='attendances')
    marker = db.relationship('User')
    
    # Ensure a student has only one attendance record per session
    __table_args__ = (
        db.UniqueConstraint('session_id', 'student_id', name='unique_attendance'),
    )
    
    def __repr__(self):
        return f'<Attendance {self.student_id} {self.status}>'
