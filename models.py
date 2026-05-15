from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), default="public")

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    department = db.Column(db.String(100))
    priority = db.Column(db.String(20))
    username = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
