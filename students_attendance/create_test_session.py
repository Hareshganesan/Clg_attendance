"""
Create a test attendance session for testing the student attendance system.
This script should be run from the project root directory.
"""

from app import create_app, db
from app.models.attendance import AttendanceSession
from app.models.course import Course, Enrollment
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.user import User
from datetime import datetime, time, timedelta, date
from werkzeug.security import generate_password_hash
import uuid
import random
import sys

def create_test_session():
    # Disable Flask's debug mode
    app = create_app()
    app.config['DEBUG'] = False
    
    with app.app_context():
        # Check database state
        print("Checking database...")
        print(f"Users: {User.query.count()}")
        print(f"Faculty: {Faculty.query.count()}")
        print(f"Students: {Student.query.count()}")
        print(f"Courses: {Course.query.count()}")
        
        # Create necessary test data if it doesn't exist
        if Course.query.count() == 0:
            print("Creating test course and faculty...")
            
            # First make sure we have a faculty user
            faculty_user = User.query.filter_by(role='faculty').first()
            if not faculty_user:
                faculty_user = User(
                    email='faculty_test@example.com',
                    username='faculty_test',
                    password_hash=generate_password_hash('password'),
                    role='faculty',
                    first_name='Test',
                    last_name='Faculty',
                    is_active=True
                )
                db.session.add(faculty_user)
                db.session.flush()
            
            # Create faculty record if it doesn't exist
            faculty = Faculty.query.first()
            if not faculty:
                faculty = Faculty(
                    user_id=faculty_user.id,
                    employee_id='FAC-TEST',
                    department='Test Department',
                    designation='Professor',
                    joining_date=datetime.now().date()
                )
                db.session.add(faculty)
                db.session.flush()
            
            # Create a test course
            course = Course(
                course_code='TEST101',
                title='Test Course',
                description='A course created for testing purposes',
                credits=3,
                faculty_id=faculty.id,
                department='Test Department',
                semester=1,
                year=2023,
                is_active=True
            )
            db.session.add(course)
            db.session.commit()
            print("Test course and faculty created!")
            
        # Now get a course and faculty for our session
        course = Course.query.first()
        faculty = Faculty.query.first()
        
        if not course or not faculty:
            print("Could not find or create course and faculty records.")
            return None
            
        # Generate a unique session code
        session_code = f"TEST-{uuid.uuid4().hex[:8].upper()}"
        
        # Create the attendance session
        today = datetime.now().date()
        start_time = time(9, 0)  # 9:00 AM
        end_time = time(10, 30)  # 10:30 AM
        
        # Check if a similar session already exists
        existing_session = AttendanceSession.query.filter_by(
            course_id=course.id,
            faculty_id=faculty.id,
            date=today
        ).first()
        
        if existing_session:
            print(f"Using existing session: {existing_session.session_code}")
            print(f"Course: {course.course_code} - {course.title}")
            print(f"Faculty: {faculty.user.first_name} {faculty.user.last_name}")
            print(f"Date: {today}")
            print(f"Active: {existing_session.is_active}")
            
            # Make sure the session is active
            if not existing_session.is_active:
                existing_session.is_active = True
                db.session.commit()
                print("Session activated!")
                
            return existing_session.session_code
            
        # Create a new attendance session
        new_session = AttendanceSession(
            course_id=course.id,
            faculty_id=faculty.id,
            date=today,
            start_time=start_time,
            end_time=end_time,
            session_code=session_code,
            is_active=True,
            location="Room 101"
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        print(f"Created new test session with code: {session_code}")
        print(f"Course: {course.course_code} - {course.title}")
        print(f"Faculty: {faculty.user.first_name} {faculty.user.last_name}")
        print(f"Date: {today}")
        
        return session_code

if __name__ == "__main__":
    session_code = create_test_session()
    print("\nUse this session code for testing:", session_code)
    print("Enter it in the 'Mark Attendance' form to test the attendance marking functionality.")
