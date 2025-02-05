from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .. import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint(
    'auth', __name__,
    template_folder='templates',
    static_folder='static'
)

# Render login page
@auth.route('/login')
def login():
    return render_template('login.html')

# Handling for login page once user submits data
@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        print("no user object")
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
              
    if not check_password_hash(user.password, password):
        print("wrong password")
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('admin_bp.admin'))


# Render signup page
@auth.route('/signup')
@login_required
def signup():
    return render_template('signup.html')

# Handling for signup page once user submits data
@auth.route('/signup', methods=['POST'])
@login_required
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        # flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # code to validate and add user to database goes here
    return redirect(url_for('auth.login'))

# Handle logout process
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
