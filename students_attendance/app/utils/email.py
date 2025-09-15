# app/utils/email.py
from flask import render_template, current_app
from flask_mail import Message
from app import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send email asynchronously
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        '[Student Attendance System] Reset Your Password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )

def send_attendance_notification(user, course, session_date):
    send_email(
        '[Student Attendance System] Attendance Recorded',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/attendance_notification.txt', 
                                  user=user, 
                                  course=course, 
                                  session_date=session_date),
        html_body=render_template('email/attendance_notification.html', 
                                 user=user, 
                                 course=course, 
                                 session_date=session_date)
    )

def send_low_attendance_warning(user, course, attendance_percentage):
    send_email(
        '[Student Attendance System] Low Attendance Warning',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user.email],
        text_body=render_template('email/low_attendance_warning.txt', 
                                  user=user, 
                                  course=course, 
                                  attendance_percentage=attendance_percentage),
        html_body=render_template('email/low_attendance_warning.html', 
                                 user=user, 
                                 course=course, 
                                 attendance_percentage=attendance_percentage)
    )
