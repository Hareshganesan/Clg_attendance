# app/controllers/admin/__init__.py
from flask import Blueprint

admin = Blueprint('admin', __name__)

from app.controllers.admin import routes
