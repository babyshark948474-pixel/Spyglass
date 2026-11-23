from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import Users, Interest
from .constants import COUNTRIES, EDUCATION_LEVELS, INTERESTS

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
        interests = [i for i in request.form.getlist('interests') if i in INTERESTS]
        email = request.form.get('email', '').strip().lower()
        password1 = request.form.get('password1', '')
        password2 = request.form.get('password2', '')

        error = None
        if not first_name or not last_name:
            error = 'Please enter your first and last name.'
        elif age is None or not 5 <= age <= 100:
            error = 'Please enter a valid age.'
        elif country not in COUNTRIES:
            error = 'Please choose a country from the list.'
        elif education not in EDUCATION_LEVELS:
            error = 'Please choose an education level from the list.'
        elif not email:
            error = 'Please enter an email address.'
        elif Users.query.filter_by(email=email).first():
            error = 'An account with that email already exists.'
        elif len(password1) < 7:
            error = 'Password must be at least 7 characters.'
        elif password1 != password2:
            error = 'Passwords must match.'
        elif not interests:
            error = 'Pick at least one interest.'

        if error:
            flash(error, category='error')
            return render_template('sign_up.html', form=request.form,
                                   countries=COUNTRIES,
                                   education_levels=EDUCATION_LEVELS,
                                   interests_list=INTERESTS)

        user = Users(first_name=first_name, last_name=last_name, age=age,
                     country=country, education_level=education, email=email)
        user.set_password(password1)

        with db.session.no_autoflush:
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

    return render_template('sign_up.html', form={}, countries=COUNTRIES,
                           education_levels=EDUCATION_LEVELS,
                           interests_list=INTERESTS)