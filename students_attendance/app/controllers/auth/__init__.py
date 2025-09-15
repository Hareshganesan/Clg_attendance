# app/controllers/auth/__init__.py
from flask import Blueprint

auth = Blueprint('auth', __name__)

from app.controllers.auth import routes
