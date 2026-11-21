import json
from datetime import date
from Website import create_app, db
from Website.models import Opportunities

app = create_app()
with app.app_context():
    if Opportunities.query.count():
        print('Already seeded, nothing to do.')
        raise SystemExit
    with open('seed_data.json', encoding='utf-8') as f:
        for r in json.load(f):
            r['deadline'] = date.fromisoformat(r['deadline']) if r['deadline'] else None
            db.session.add(Opportunities(**r))
    db.session.commit()
    print('Seeded.')