# app/controllers/faculty/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import date, time

class CreateAttendanceSessionForm(FlaskForm):
    course_id = SelectField('Course', validators=[DataRequired()], coerce=int)
    date = DateField('Date', validators=[DataRequired()], format='%Y-%m-%d')
    start_time = TimeField('Start Time', validators=[DataRequired()], format='%H:%M')
    end_time = TimeField('End Time', validators=[DataRequired()], format='%H:%M')
    location = StringField('Location', validators=[Length(max=100)])
    notes = TextAreaField('Notes')
    submit = SubmitField('Create Session')
    
    def validate_date(self, date_field):
        if date_field.data < date.today():
            raise ValidationError('Date cannot be in the past.')
    
    def validate_end_time(self, end_time):
        if self.start_time.data and end_time.data and end_time.data <= self.start_time.data:
            raise ValidationError('End time must be after start time.')

class MarkAttendanceForm(FlaskForm):
    submit = SubmitField('Save Attendance')
