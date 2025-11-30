from flask import jsonify
from flask import flash
from flask import json
from flask import request
from flask import Blueprint
import os
from flask_login import current_user, login_required, logout_user
from models.model import User
from models.connection import db
import requests
from flask import render_template, redirect, url_for
from routes.auth import user_has_role 

app = Blueprint('user', __name__)

@user_has_role('admin')
@login_required
@app.route('/user/<username>')
def show_user_profile(username):
    return f'User: {username}'

@user_has_role('admin')
@login_required
@app.route('/user/<int:user_id>')
def show_user_from_id(user_id):
    stmt = db.select(User).filter_by(id=user_id)
    user = db.session.execute(stmt).scalar_one_or_none()

    return jsonify(user.to_dict()), 200

@user_has_role('admin')
@login_required
@app.route('/user', methods=['POST'])
def save_user():
    
    username = request.form["username"]
    email = request.form["email"]    
    password = request.form["password"]

    if not username:
        flash('Invalid username')
        return redirect(url_for('auth.admin_dashboard'))
    if not email:
        flash('Invalid email')
        return redirect(url_for('auth.admin_dashboard'))
    if not password:
        flash('Invalid password')
        return redirect(url_for('auth.admin_dashboard'))                
    
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    if user: 
        # if a user is found, we want to redirect back to signup page so user can try again
        # display some kind of error
        flash('User with this email address already exists')
        return redirect(url_for('auth.admin_dashboard'))
    try:  
        user = User(username=username, email=email)
        user.set_password(password)  # Imposta la password criptata
        db.session.add(user)
        db.session.commit()
        response = user.to_dict()
        with open('users_created_by_admins.txt', 'a') as file:
            file.write(str(response) + '\n')

        return render_template('admin_dashboard.html', users=User.query.all()), 201
    except Exception as e:
        db.session.rollback()
        error = str(e.args)
        return render_template('admin_dashboard.html', users=User.query.all(),error=error), 500


@user_has_role('admin')
@login_required
@app.route('/users')
def get_users():
    data = []
    users = User.query.all()
    for user in users:
        data.append(user.to_dict())
    return jsonify(data)

@app.route('/delete', methods=['POST'])
@login_required
def delete():
    if current_user.has_role('admin'):
        flash('Admin cant be deleted from database.')
        return redirect(url_for('auth.profile'))
    password = request.form.get('password')
    if not current_user.check_password(password):
        flash('Password incorrect. Cannot delete account.')
        return redirect(url_for('auth.profile'))
    user_id = current_user.id
    logout_user()
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Your account is now deleted.')
    else:
        flash('User not found.')
    return redirect(url_for('auth.signup'))

@app.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@user_has_role('admin')
def admin_delete(user_id):
    user = User.query.get(user_id)
    if user:
        if user.has_role('admin'):
            flash('Admin cant be deleted from database.')
            return redirect(url_for('auth.admin_dashboard'))
        db.session.delete(user)
        db.session.commit()
        flash('User deleted.')
    else:
        flash('User not found.')
    return redirect(url_for('auth.admin_dashboard'))

@user_has_role('admin','user')
@login_required
@app.route('/users/update/<int:user_id>', methods=['GET'])
def update_user_email_by_id_view(user_id):
    return render_template('update_user_email.html', user_id=user_id)

@user_has_role('admin','user')
@login_required
@app.route('/users/update/<int:user_id>/email', methods=['GET'])
def update_user_email_by_id_get(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Utente non trovato.')
        return redirect(url_for('auth.admin_dashboard'))
    
    return render_template('update_user_email.html', user=user)

@user_has_role('admin','user')
@login_required
@app.route('/users/update/<int:user_id>', methods=['POST'])
def update_user_email_by_id(user_id):
    new_email = request.form.get('email')
    if not new_email:
        flash('Email non valida.')
        return redirect(url_for('update_user_email_by_id_view', user_id=user_id))
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user and existing_user.id != user_id:
        flash('Questa email è già in uso.')
        return redirect(url_for('update_user_email_by_id_view', user_id=user_id))

    user = User.query.get(user_id)
    if not user:
        flash('Utente non trovato.')
        return redirect(url_for('auth.admin_dashboard'))

    try:
        user.email = new_email
        db.session.commit()
        flash('Email aggiornata con successo.')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'aggiornamento: {str(e)}')

    return redirect(url_for('auth.profile'))
