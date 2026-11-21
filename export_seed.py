import json
from Website import create_app
from Website.models import Opportunities

app = create_app()
with app.app_context():
    rows = [{
        'title': o.title, 'opportunity_type': o.opportunity_type,
        'category': o.category, 'country': o.country,
        'min_age': o.min_age, 'max_age': o.max_age,
        'education_level': o.education_level,
        'opportunity_description': o.opportunity_description,
        'application_link': o.application_link,
        'deadline': o.deadline.isoformat() if o.deadline else None,
    } for o in Opportunities.query.all()]

with open('seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)
print(len(rows), 'opportunities exported')