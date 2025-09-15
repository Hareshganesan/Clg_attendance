# app/controllers/admin/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.course import Course
from datetime import datetime

class AddFacultyForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    department = StringField('Department', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    joining_date = DateField('Joining Date', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.utcnow)
    submit = SubmitField('Add Faculty')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')
    
    def validate_employee_id(self, employee_id):
        faculty = Faculty.query.filter_by(employee_id=employee_id.data).first()
        if faculty:
            raise ValidationError('Employee ID is already registered. Please check your details.')

class AddStudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    roll_number = StringField('Roll Number', validators=[DataRequired()])
    enrollment_year = IntegerField('Enrollment Year', validators=[DataRequired(), NumberRange(min=2000, max=datetime.utcnow().year)])
    department = StringField('Department', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired(), NumberRange(min=1, max=8)])
    section = StringField('Section')
    submit = SubmitField('Add Student')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different one.')
    
    def validate_roll_number(self, roll_number):
        student = Student.query.filter_by(roll_number=roll_number.data).first()
        if student:
            raise ValidationError('Roll number is already registered. Please check your details.')

class AddCourseForm(FlaskForm):
    course_code = StringField('Course Code', validators=[DataRequired(), Length(min=2, max=20)])
    title = StringField('Course Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    credits = IntegerField('Credits', validators=[DataRequired(), NumberRange(min=1, max=6)])
    faculty_id = SelectField('Faculty', validators=[DataRequired()], coerce=int)
    department = StringField('Department', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired(), NumberRange(min=1, max=8)])
    year = IntegerField('Year', validators=[DataRequired()])
    is_active = BooleanField('Active Course', default=True)
    submit = SubmitField('Add Course')
    
    def validate_course_code(self, course_code):
        course = Course.query.filter_by(course_code=course_code.data).first()
        if course:
            raise ValidationError('Course code is already in use. Please choose a different one.')

class EditCourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    credits = IntegerField('Credits', validators=[DataRequired(), NumberRange(min=1, max=6)])
    faculty_id = SelectField('Faculty', validators=[DataRequired()], coerce=int)
    department = StringField('Department', validators=[DataRequired()])
    semester = IntegerField('Semester', validators=[DataRequired(), NumberRange(min=1, max=8)])
    year = IntegerField('Year', validators=[DataRequired()])
    is_active = BooleanField('Active Course')
    submit = SubmitField('Update Course')

class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_active = BooleanField('Active User')
    submit = SubmitField('Update User')
