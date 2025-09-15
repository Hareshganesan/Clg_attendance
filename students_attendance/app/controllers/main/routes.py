# app/controllers/main/routes.py
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app.controllers.main import main
from app import db

@main.route('/')
def index():
    return render_template('main/index.html', title='Home')

@main.route('/about')
def about():
    return render_template('main/about.html', title='About')

@main.route('/contact')
def contact():
    return render_template('main/contact.html', title='Contact')

@main.route('/profile')
@login_required
def profile():
    return render_template('main/profile.html', title='Profile')

@main.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    from app.controllers.main.forms import ProfileUpdateForm
    
    form = ProfileUpdateForm()
    if form.validate_on_submit():
        # Update user information
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        
        # Save profile picture if provided
        if form.profile_picture.data:
            from app.utils.save_picture import save_profile_picture
            picture_filename = save_profile_picture(form.profile_picture.data)
            current_user.profile_image = picture_filename
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
    
    return render_template('main/edit_profile.html', title='Edit Profile', form=form)
