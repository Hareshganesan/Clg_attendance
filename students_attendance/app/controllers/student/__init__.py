# app/controllers/student/__init__.py
from flask import Blueprint

student = Blueprint('student', __name__)

from app.controllers.student import routes
