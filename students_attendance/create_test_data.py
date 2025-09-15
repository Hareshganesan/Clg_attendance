"""
Create test data for the student attendance system.
This script should be run from the project root directory.
"""

from app import create_app, db
from app.models.attendance import AttendanceSession, Attendance
from app.models.course import Course, Enrollment
from app.models.faculty import Faculty
from app.models.student import Student
from app.models.user import User
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash
import random

def create_test_data():
    app = create_app()
    app.config['DEBUG'] = False
    
    with app.app_context():
        # Clear existing data (optional)
        # db.drop_all()
        # db.create_all()
        
        # Check if we already have users
        if User.query.count() > 0:
            print("Data already exists. Skipping...")
            return
        
        print("Creating test data...")
        
        # Create admin user
        admin = User(
            email='admin@example.com',
            username='admin',
            password_hash=generate_password_hash('password'),
            role='admin',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        db.session.add(admin)
        
        # Create faculty users
        faculty_data = [
            {
                'email': 'faculty1@example.com',
                'username': 'faculty1',
                'password': 'password',
                'first_name': 'John',
                'last_name': 'Smith',
                'employee_id': 'FAC001',
                'department': 'Computer Science',
                'designation': 'Assistant Professor',
                'joining_date': date(2020, 7, 15)
            },
            {
                'email': 'faculty2@example.com',
                'username': 'faculty2',
                'password': 'password',
                'first_name': 'Mary',
                'last_name': 'Johnson',
                'employee_id': 'FAC002',
                'department': 'Mathematics',
                'designation': 'Associate Professor',
                'joining_date': date(2018, 5, 10)
            }
        ]
        
        faculty_list = []
        for f_data in faculty_data:
            faculty_user = User(
                email=f_data['email'],
                username=f_data['username'],
                password_hash=generate_password_hash(f_data['password']),
                role='faculty',
                first_name=f_data['first_name'],
                last_name=f_data['last_name'],
                is_active=True
            )
            db.session.add(faculty_user)
            db.session.flush()  # Get the user ID
            
            faculty = Faculty(
                user_id=faculty_user.id,
                employee_id=f_data['employee_id'],
                department=f_data['department'],
                designation=f_data['designation'],
                joining_date=f_data['joining_date']
            )
            db.session.add(faculty)
            faculty_list.append(faculty)
        
        # Create student users
        student_data = [
            {
                'email': 'student1@example.com',
                'username': 'student1',
                'password': 'password',
                'first_name': 'Alex',
                'last_name': 'Jones',
                'roll_number': 'STU001',
                'enrollment_year': 2023,
                'department': 'Computer Science',
                'semester': 3,
                'section': 'A'
            },
            {
                'email': 'student2@example.com',
                'username': 'student2',
                'password': 'password',
                'first_name': 'Sarah',
                'last_name': 'Davis',
                'roll_number': 'STU002',
                'enrollment_year': 2022,
                'department': 'Mathematics',
                'semester': 5,
                'section': 'B'
            },
            {
                'email': 'student3@example.com',
                'username': 'student3',
                'password': 'password',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'roll_number': 'STU003',
                'enrollment_year': 2023,
                'department': 'Computer Science',
                'semester': 3,
                'section': 'A'
            }
        ]
        
        student_list = []
        for s_data in student_data:
            student_user = User(
                email=s_data['email'],
                username=s_data['username'],
                password_hash=generate_password_hash(s_data['password']),
                role='student',
                first_name=s_data['first_name'],
                last_name=s_data['last_name'],
                is_active=True
            )
            db.session.add(student_user)
            db.session.flush()  # Get the user ID
            
            student = Student(
                user_id=student_user.id,
                roll_number=s_data['roll_number'],
                enrollment_year=s_data['enrollment_year'],
                department=s_data['department'],
                semester=s_data['semester'],
                section=s_data['section']
            )
            db.session.add(student)
            student_list.append(student)
        
        # Create courses
        course_data = [
            {
                'course_code': 'CS101',
                'name': 'Introduction to Programming',
                'description': 'A beginner-friendly course covering the basics of programming.',
                'credits': 3,
                'faculty_id': 1
            },
            {
                'course_code': 'CS201',
                'name': 'Data Structures and Algorithms',
                'description': 'Learn about common data structures and algorithm design techniques.',
                'credits': 4,
                'faculty_id': 1
            },
            {
                'course_code': 'MATH101',
                'name': 'Calculus I',
                'description': 'Introduction to differential and integral calculus.',
                'credits': 3,
                'faculty_id': 2
            }
        ]
        
        course_list = []
        for c_data in course_data:
            course = Course(
                course_code=c_data['course_code'],
                name=c_data['name'],
                description=c_data['description'],
                credits=c_data['credits'],
                faculty_id=c_data['faculty_id']
            )
            db.session.add(course)
            course_list.append(course)
        
        db.session.commit()
        
        # Enroll students in courses
        for student in student_list:
            for course in course_list:
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_date=datetime.now().date(),
                    is_active=True
                )
                db.session.add(enrollment)
        
        db.session.commit()
        
        print("Test data created successfully!")
        print("\nLogin credentials:")
        print("Admin: admin@example.com / password")
        print("Faculty 1: faculty1@example.com / password")
        print("Faculty 2: faculty2@example.com / password")
        print("Student 1: student1@example.com / password")
        print("Student 2: student2@example.com / password")
        print("Student 3: student3@example.com / password")

if __name__ == "__main__":
    create_test_data()
