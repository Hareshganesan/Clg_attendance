# app/utils/save_picture.py
import os
import secrets
from PIL import Image
from flask import current_app

def save_profile_picture(form_picture):
    """Save profile picture with a random name and resize it"""
    # Generate a random name for the picture
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_extension
    
    # Define the path where the picture will be saved
    pictures_path = os.path.join(current_app.root_path, 'static/images/profile_pics')
    
    # Create directory if it doesn't exist
    os.makedirs(pictures_path, exist_ok=True)
    
    picture_path = os.path.join(pictures_path, picture_filename)
    
    # Resize the image to save space and maintain quality
    output_size = (150, 150)
    img = Image.open(form_picture)
    img.thumbnail(output_size)
    
    # Save the picture
    img.save(picture_path)
    
    return picture_filename
