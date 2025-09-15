# app/controllers/faculty/__init__.py
from flask import Blueprint

faculty = Blueprint('faculty', __name__)

from app.controllers.faculty import routes
