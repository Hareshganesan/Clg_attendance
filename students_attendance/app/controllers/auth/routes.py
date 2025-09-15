# app/controllers/auth/routes.py
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.controllers.auth import auth
from app.controllers.auth.forms import (
    LoginForm, RegistrationForm, ResetPasswordRequestForm, 
    ResetPasswordForm, ChangePasswordForm
)
from app.utils.email import send_password_reset_email

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # Redirect based on user role
            if not next_page or next_page.startswith('/'):
                if user.role == 'admin':
                    next_page = url_for('admin.dashboard')
                elif user.role == 'faculty':
                    next_page = url_for('faculty.dashboard')
                elif user.role == 'student':
                    next_page = url_for('student.dashboard')
                else:
                    next_page = url_for('main.index')
                
            return redirect(next_page)
        else:
            flash('Login unsuccessful. Please check email and password.', 'danger')
    
    return render_template('auth/login.html', title='Login', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='student'  # Default role is student
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
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('auth/change_password.html', title='Change Password', form=form)
