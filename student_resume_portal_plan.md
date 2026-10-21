# Technical Specification & Project Plan: Student Resume Portal

An end-to-end architectural roadmap for a multi-profile student resume application built strictly with **Python**, **Flask**, and **Jinja2**.

---

## 1. System Overview

The application enables students to register, manage multiple tailored resumes (e.g., *Frontend Developer*, *Data Analyst*), preview them across customizable layouts, and export them as print-ready A4 PDFs. The system is designed to allow modular theme extensions and future paywall gates without restructuring database entities.

```
[ Auth / Registration ]
           │
           ▼
[ Student Dashboard ] ──── Manage multiple resume profiles
           │
   ┌───────┴────────────────────────┐
   ▼                                ▼
[ Profile Builder & Editor ]   [ Dynamic Theme Preview ]
 - Basic details & links        - Dynamic Jinja layouts
 - Work history (multi-entry)   - Theme selector (Classic, Modern, etc.)
 - Education (multi-entry)      - Print-to-PDF / Server PDF export
 - Skills & tags                - [Phase 4] Paywall / Credit Verification
```

---

## 2. Directory Structure

```text
flask-student-resumes/
│
├── app.py                         # Application factory, routes, and error handlers
├── config.py                      # Environment configs (Secret keys, DB URIs)
├── models.py                      # SQLAlchemy database schemas
├── requirements.txt               # Project dependencies
├── .gitignore
│
├── static/
│   ├── css/
│   │   ├── dashboard.css          # Styling for student portal, auth, and forms
│   │   └── themes/
│   │       ├── classic.css        # Initial clean ATS-compliant theme
│   │       └── modern.css         # Future theme styles
│   └── js/
│       ├── dynamic_fields.js      # Form controls (add/remove experience & education)
│       └── print_helper.js        # Trigger browser print dialog for PDF export
│
└── templates/
    ├── base.html                  # Core layout shell (Nav, alerts, container)
    ├── auth/
    │   ├── login.html             # User authentication form
    │   └── register.html          # Account registration form
    ├── dashboard/
    │   ├── index.html             # Profile list + "Create New Profile" card
    │   ├── profile_form.html      # Multi-section editor
    │   └── checkout.html          # [Phase 4] Payment / upgrade placeholder
    └── resume_themes/
        ├── _resume_base.html      # Isolated print shell (no portal navbar/sidebar)
        └── classic.html           # Initial standard Jinja resume template
```

---

## 3. Database Schema (`models.py`)

The application models a **1-to-many relationship** from a `User` to their `ResumeProfile` entities, with cascade deletes handling dynamic subsections.

### Schema Relationships

| Model | Parent | Key Attributes | Notes |
|---|---|---|---|
| **`User`** | — | `id`, `email`, `password_hash`, `full_name`, `is_premium`, `downloads_remaining` | Controls login and access rights |
| **`ResumeProfile`** | `User` | `id`, `user_id`, `profile_title`, `summary`, `theme_name`, `phone`, `location`, links | Base profile entity |
| **`Experience`** | `ResumeProfile` | `id`, `resume_id`, `company`, `role`, `duration`, `description` | Multi-record work history |
| **`Education`** | `ResumeProfile` | `id`, `resume_id`, `institution`, `degree`, `duration`, `score` | Multi-record academic history |
| **`Skill`** | `ResumeProfile` | `id`, `resume_id`, `name`, `category` | Categorized technical competencies |

### Model Implementation

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Billing fields (for Phase 4)
    is_premium = db.Column(db.Boolean, default=False)
    downloads_remaining = db.Column(db.Integer, default=1)  # 1 free export
    
    profiles = db.relationship('ResumeProfile', backref='owner', lazy=True, cascade="all, delete-orphan")

class ResumeProfile(db.Model):
    __tablename__ = 'resume_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    profile_title = db.Column(db.String(100), nullable=False)  # e.g., "Software Engineer"
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30))
    location = db.Column(db.String(100))
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    portfolio_url = db.Column(db.String(200))
    summary = db.Column(db.Text)
    
    theme_name = db.Column(db.String(50), default='classic')  # Controls Jinja template selection
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    name = db.Column(db.String(50), nullable=False)
```

---

## 4. Phased Delivery Roadmap

```
Phase 1: Foundation (Auth & CRUD)
   └─ Phase 2: Resume Engine & PDF Export
         └─ Phase 3: Modular Theme Engine
               └─ Phase 4: Monetization / Paywall Gate
```

### Phase 1: Authentication & Multi-Profile Management
* Configure `Flask-Login` session management and `Werkzeug` secure hashing.
* Build the student dashboard listing all created resumes.
* Create the multi-section profile builder form.
* Implement dynamic JavaScript helpers (`dynamic_fields.js`) enabling users to append and remove arbitrary numbers of employment or degree records prior to submission.

### Phase 2: Initial Template & PDF Rendering Engine
* Implement the first standardized template (`templates/resume_themes/classic.html`).
* Configure print media stylesheets (`@media print` rules) to format output precisely to A4 dimensions, strip web UI elements, and prevent bad page breaks.
* Provide an immediate "Download / Print PDF" action via `window.print()` (client-side native rendering) with no external server-side binary overhead.

### Phase 3: Modular Theme Extension
* Isolate resume styling into independent CSS sheets (`static/css/themes/*.css`) and Jinja fragments.
* Implement a theme switcher in the dashboard, enabling users to preview the exact same profile data rendered through alternative templates:
  ```python
  @app.route('/resume/<int:profile_id>/preview')
  @login_required
  def preview_resume(profile_id):
      profile = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
      return render_template(f'resume_themes/{profile.theme_name}.html', profile=profile)
  ```

### Phase 4: Download Paywall & Monetization
* Restrict the export route with permission checks:
  ```python
  @app.route('/resume/<int:profile_id>/export')
  @login_required
  def export_resume(profile_id):
      profile = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
      
      # Paywall check
      if not current_user.is_premium and current_user.downloads_remaining <= 0:
          return redirect(url_for('pricing', needed_for=profile.id))
      
      # Decrement available balance if on non-premium tier
      if not current_user.is_premium:
          current_user.downloads_remaining -= 1
          db.session.commit()
          
      return render_template(f'resume_themes/{profile.theme_name}.html', profile=profile, auto_print=True)
  ```
* Integrate payment processing (Razorpay, Stripe, or manual admin unlock) to update user records via webhooks.

---

## 5. Technology Stack Specifications

* **Language:** Python 3.10+
* **Framework:** Flask 3.0+
* **Templating:** Jinja2 (Built into Flask)
* **Database Layer:** SQLAlchemy via `Flask-SQLAlchemy`
* **Session Management:** `Flask-Login`
* **Styling:** Vanilla CSS with custom properties and CSS Grid/Flexbox
* **WSGI Production Server:** Gunicorn

```text
# requirements.txt
Flask>=3.0.0
Flask-SQLAlchemy>=3.1.0
Flask-Login>=0.6.3
Werkzeug>=3.0.0
gunicorn>=21.0.0
```