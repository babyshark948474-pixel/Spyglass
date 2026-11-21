from flask import Blueprint, render_template, request, flash, redirect, url_for
from . import db
from .models import Opportunities, Submissions
from datetime import date, timedelta, datetime
from sqlalchemy import or_
from .constants import COUNTRIES, EDUCATION_LEVELS, INTERESTS, OPPORTUNITY_TYPES

views = Blueprint('views', __name__)

TOTAL_CRITERIA = 2
MIN_SCORE = 1

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        age = request.form.get('age', type=int)
        country = request.form.get('country')
        education = request.form.get('education')
        interests =[i for i in  request.form.getlist('interests') if i in INTERESTS] 

        if age is None or not 5 <= age <= 100:
            flash('Please enter a valid age.', category='error')
            return redirect(url_for('views.home'))
        if country not in COUNTRIES: 
            flash('Please choose a country from the list', category='error')
            return redirect(url_for('views.home'))
        if education not in EDUCATION_LEVELS:
            flash('Please choose an education level from the list provided', category='error')
            return redirect(url_for('views.home'))

        today = date.today()
        all_opportunities = Opportunities.query.filter(or_(Opportunities.deadline == None, Opportunities.deadline >= today)).all()

        scored_opportunities = []

        for opp in all_opportunities:
            if opp.country not in (country, 'Caribbean'):
                continue
            if opp.min_age is not None and age < opp.min_age:
                continue
            if opp.max_age is not None and age > opp.max_age:
                continue
            if opp.education_level is not None and opp.education_level != education:
                continue
            score = 0
            matched_criteria = []

            if opp.country == country:
                score += 1
                matched_criteria.append('Country')
            elif opp.country == 'Caribbean':
                score += 1
                matched_criteria.append('Caribbean-wide')

            if opp.category in interests:
                score += 1
                matched_criteria.append('Interest')


            if score >= MIN_SCORE:  
                scored_opportunities.append({
                    'opportunity': opp,
                    'score': score,
                    'matched_criteria': matched_criteria,
                    'total': TOTAL_CRITERIA,
                })

        scored_opportunities.sort(key=lambda x: x['score'], reverse=True)
        return render_template('results.html', results=scored_opportunities)

    return render_template('home.html', countries = COUNTRIES, education_levels=EDUCATION_LEVELS, interests_list = INTERESTS)

@views.route('/browse')
def browse():
    q = request.args.get('q', '').strip()
    opp_type = request.args.get('type', '')
    category = request.args.get('category', '')
    country = request.args.get('country', '')
    deadline = request.args.get('deadline', '')

    today = date.today()
    query = Opportunities.query.filter(
        or_(Opportunities.deadline.is_(None), Opportunities.deadline >= today)
    )

    if q:
        like = f'%{q}%'
        query = query.filter(or_(
            Opportunities.title.ilike(like),
            Opportunities.opportunity_description.ilike(like),
        ))

    if opp_type:
        query = query.filter(Opportunities.opportunity_type == opp_type)

    if category:
        query = query.filter(Opportunities.category == category)

    if country:
        query = query.filter(or_(
            Opportunities.country == country,
            Opportunities.country == 'Caribbean',
        ))

    if deadline.isdigit():
        cutoff = today + timedelta(days=int(deadline))
        query = query.filter(Opportunities.deadline <= cutoff)

    results = query.order_by(
        Opportunities.deadline.is_(None), Opportunities.deadline
    ).all()
   
    types = [r[0] for r in db.session.query(Opportunities.opportunity_type)
             .distinct().order_by(Opportunities.opportunity_type)]
    categories = [r[0] for r in db.session.query(Opportunities.category)
                  .distinct().order_by(Opportunities.category)]
    countries = [r[0] for r in db.session.query(Opportunities.country)
                 .distinct().order_by(Opportunities.country) if r[0] != 'Caribbean']

    return render_template(
        'browse.html', results=results,
        types=types, categories=categories, countries=countries,
        q=q, opp_type=opp_type, category=category,
        country=country, deadline=deadline,
    )

@views.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        f = request.form
        org = f.get('organization_name', '').strip()
        title = f.get('title', '').strip()
        opp_type = f.get('opportunity_type')
        category = f.get('category')
        country = f.get('country')
        education = f.get('education_level') or None   
        description = f.get('description', '').strip()
        link = f.get('application_link', '').strip()
        min_age = f.get('min_age', type=int)
        max_age = f.get('max_age', type=int)

        deadline = None
        if f.get('deadline'):
            try:
                deadline = datetime.strptime(f['deadline'], '%Y-%m-%d').date()
            except ValueError:
                flash('That deadline is not a valid date.', category='error')
                return render_template('submit.html', **form_options(), form=f)

        error = None
        if not org or not title:
            error = 'Organization name and title are required.'
        elif opp_type not in OPPORTUNITY_TYPES or category not in INTERESTS \
                or (country not in COUNTRIES and country != 'Caribbean'):
            error = 'Please choose a type, category and country from the lists.'
        elif min_age is not None and max_age is not None and min_age > max_age:
            error = 'Minimum age cannot be greater than maximum age.'
        elif deadline and deadline < date.today():
            error = 'The deadline has already passed.'
        elif not link.startswith(('http://', 'https://')):
            error = 'The application link must start with http:// or https://'

        if error:
            flash(error, category='error')
            return render_template('submit.html', **form_options(), form=f)

        db.session.add(Submissions(
            organization_name=org, title=title, opportunity_type=opp_type,
            category=category, country=country, min_age=min_age, max_age=max_age,
            education_level=education, description=description,
            application_link=link, deadline=deadline,
        ))
        db.session.commit()
        flash('Thank you! Your opportunity was submitted and will appear once it is reviewed.',
              category='success')
        return redirect(url_for('views.submit'))

    return render_template('submit.html', **form_options(), form={})


def form_options():
    return dict(countries=COUNTRIES, education_levels=EDUCATION_LEVELS,
                categories=INTERESTS, types=OPPORTUNITY_TYPES)
         
        


