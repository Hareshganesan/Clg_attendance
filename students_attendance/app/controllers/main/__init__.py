# app/controllers/main/__init__.py
from flask import Blueprint

main = Blueprint('main', __name__)

from app.controllers.main import routes
