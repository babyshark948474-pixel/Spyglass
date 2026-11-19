from flask import Blueprint, render_template, request
from . import db
from .models import Opportunities
from datetime import date, timedelta
from sqlalchemy import or_
from .constants import COUNTRIES, EDUCATION_LEVELS, INTERESTS

views = Blueprint('views', __name__)

TOTAL_CRITERIA = 2
MIN_SCORE = 1

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        age = request.form.get('age', type=int)
        country = request.form.get('country')
        education = request.form.get('education')
        interests = request.form.getlist('interests')  

        today = date.today()
        all_opportunities = Opportunities.query.filter(or_(Opportunities.deadline == None, Opportunities.deadline >= today)).all()

        scored_opportunities = []

        for opp in all_opportunities:
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

         
        


