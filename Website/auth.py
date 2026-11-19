from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import Users, Interest

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = Users.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('Welcome back!', category='success')
            return redirect(url_for('views.home'))
        flash('Incorrect email or password.', category='error')

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        first_name = request.form.get('firstName', '').strip()
        last_name = request.form.get('lastName', '').strip()
        age = request.form.get('age', type=int)
        country = request.form.get('country')
        education = request.form.get('education')
        interests = request.form.getlist('interests')
        email = request.form.get('email', '').strip().lower()
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')

        if Users.query.filter_by(email=email).first():
            flash('An account with that email already exists.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif password1 != password2:
            flash('Passwords must match.', category='error')
        elif not interests:
            flash('Pick at least one interest.', category='error')
        else:
            user = Users(first_name=first_name, last_name=last_name, age=age,
                         country=country, education_level=education, email=email)
            user.set_password(password1)

            for name in interests:
                interest = Interest.query.filter_by(interests=name).first()
                if not interest:
                    interest = Interest(interests=name)
                    db.session.add(interest)
                user.interest.append(interest)

            db.session.add(user)
            db.session.commit()

            login_user(user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html')
