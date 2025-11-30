from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import current_app   # definisce il contesto del modulo
from flask_login import current_user, login_user, logout_user, login_required  # https://flask-login.readthedocs.io/en/latest/#flask_login.login_user
from functools import wraps
from flask import abort
from models.connection import db
from models.model import *

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    # shows the login form page
    return render_template('auth/login.html')

@auth.route('/signup')
def signup():
    # shows the signup form page
    return render_template('auth/signup.html')

@auth.route('/profile')
@login_required
def profile():
    # shows the signup form page
    return render_template('auth/profile.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['POST'])
def login_post():
    # manages the login form post request
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not user.check_password(password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user)
    return redirect(url_for('auth.profile'))    

@auth.route('/signup', methods=['POST'])
def signup_post():
    # signup input validation and logic
    #TODO verify password strenght
    username = request.form["username"] #as an alternative use request.form.get("username")
    email = request.form["email"]    
    password = request.form["password"]

    if not username:
        flash('Invalid username')
        return redirect(url_for('auth.signup'))
    if not email:
        flash('Invalid email')
        return redirect(url_for('auth.signup'))
    if not password:
        flash('Invalid password')
        return redirect(url_for('auth.signup'))                
    
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if user: 
        # if a user is found, we want to redirect back to signup page so user can try again
        # display some kind of error
        flash('User with this email address already exists')
        return redirect(url_for('auth.signup'))

    user = User(username=username, email=email)
    user.set_password(password)  # Imposta la password criptata
    db.session.add(user)  # equivalente a INSERT
    db.session.commit()
    # login_user(user)
    return redirect(url_for('auth.login'))

def user_has_role(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Devi essere autenticato per accedere a questa pagina.")
                return redirect(url_for('login'))
            if not any(current_user.has_role(role) for role in role_names):
                flash("Non hai il permesso per accedere a questa pagina.")
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth.route('/dashboard')
@login_required
@user_has_role('admin')
def admin_dashboard():
    if not current_user.has_role('admin'):
        flash("Accesso non autorizzato!")
        return render_template('dashboard.html')
    users= User.query.all()
    return render_template('admin_dashboard.html', users=users)
