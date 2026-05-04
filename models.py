from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    reset_token = db.Column(db.String(200), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    opportunities = db.relationship('Opportunity', backref='user', lazy=True)


class Opportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)

    skills = db.Column(db.Text, nullable=False)
    future_opportunities = db.Column(db.Text, nullable=False)

    max_applicants = db.Column(db.Integer, nullable=True)