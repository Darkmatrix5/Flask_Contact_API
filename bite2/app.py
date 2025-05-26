from flask import Flask, request, jsonify, render_template 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'contacts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.app_context().push()

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phoneNumber = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    linkedId = db.Column(db.Integer, nullable=True)
    linkPrecedence = db.Column(db.String, default='primary')
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    deletedAt = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Contact {self.id}>"

@app.route('/')
def home():
    return render_template('form.html')

@app.route('/identify', methods=['POST'])
def identify():
    data = request.json
    email = data.get("email")
    phone = data.get("phoneNumber")

    if not email and not phone:
        return jsonify({"error": "At least one of email or phoneNumber must be provided"}), 400

    matches = Contact.query.filter((Contact.email == email) | (Contact.phoneNumber == phone)).all()

    if not matches:
        new_contact = Contact(email=email, phoneNumber=phone)
        db.session.add(new_contact)
        db.session.commit()
        return jsonify({
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [new_contact.email] if new_contact.email else [],
                "phoneNumbers": [new_contact.phoneNumber] if new_contact.phoneNumber else [],
                "secondaryContactIds": []
            }
        })

    related = set()

    def link(c):
        if c in related:
            return
        related.add(c)
        if c.linkPrecedence == 'secondary' and c.linkedId:
            main = Contact.query.get(c.linkedId)
            if main:
                link(main)
        subs = Contact.query.filter_by(linkedId=c.id).all()
        for s in subs:
            link(s)

    for m in matches:
        link(m)

    primary = min(related, key=lambda x: x.createdAt)
    primary_id = primary.id

    emails = {c.email for c in related if c.email}
    phones = {c.phoneNumber for c in related if c.phoneNumber}
    secondary_ids = []

    for c in related:
        if c.id != primary_id:
            if c.linkPrecedence != 'secondary' or c.linkedId != primary_id:
                c.linkPrecedence = 'secondary'
                c.linkedId = primary_id
                c.updatedAt = datetime.utcnow()
                db.session.add(c)
            secondary_ids.append(c.id)

    if not any(c.email == email and c.phoneNumber == phone for c in related):
        extra = Contact(email=email, phoneNumber=phone, linkPrecedence='secondary', linkedId=primary_id)
        db.session.add(extra)
        db.session.commit()
        if extra.email: emails.add(extra.email)
        if extra.phoneNumber: phones.add(extra.phoneNumber)
        secondary_ids.append(extra.id)

    db.session.commit()

    return jsonify({
        "contact": {
            "primaryContactId": primary_id,
            "emails": ([primary.email] if primary.email else []) + sorted(e for e in emails if e != primary.email),
            "phoneNumbers": ([primary.phoneNumber] if primary.phoneNumber else []) + sorted(p for p in phones if p != primary.phoneNumber),
            "secondaryContactIds": sorted(secondary_ids)
        }
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
