from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

def get_utc_now():
    return datetime.now(timezone.utc)

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    # Billing fields (Phase 4 ready)
    is_premium = db.Column(db.Boolean, default=False)
    downloads_remaining = db.Column(db.Integer, default=1)  # 1 free export

    profiles = db.relationship('ResumeProfile', backref='owner', lazy=True, cascade="all, delete-orphan")


class ResumeProfile(db.Model):
    __tablename__ = 'resume_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    profile_title = db.Column(db.String(100), nullable=False)  # e.g., "Frontend Developer"
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    location = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    portfolio_url = db.Column(db.String(200))
    summary = db.Column(db.Text)

    theme_name = db.Column(db.String(50), default='classic')  # Controls Jinja template selection
    updated_at = db.Column(db.DateTime, default=get_utc_now, onupdate=get_utc_now)

    experiences = db.relationship('Experience', backref='resume', lazy=True, cascade="all, delete-orphan")
    education = db.relationship('Education', backref='resume', lazy=True, cascade="all, delete-orphan")
    skills = db.relationship('Skill', backref='resume', lazy=True, cascade="all, delete-orphan")



class Experience(db.Model):
    __tablename__ = 'experiences'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume_profiles.id'), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(60))
    description = db.Column(db.Text)  # Stores bullet points separated by newlines


class Education(db.Model):
    __tablename__ = 'education'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume_profiles.id'), nullable=False)
    institution = db.Column(db.String(150), nullable=False)
    degree = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(60))
    score = db.Column(db.String(30))  # e.g., "8.8 CGPA" or "82%"


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume_profiles.id'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
