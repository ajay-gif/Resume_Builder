import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import config_by_name, DevelopmentConfig
from models import db, User, ResumeProfile, Experience, Education, Skill
from email_service import send_password_reset_email

def create_app(config_mode=None):
    """Application factory for Flask app."""
    if config_mode is None:
        config_mode = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_mode, DevelopmentConfig))

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    # --- Error Handlers ---
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', not_found=True), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', server_error=True), 500

    # --- Authentication Routes ---

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            if not full_name or not email or not password:
                flash('Please fill in all required fields.', 'danger')
                return redirect(url_for('register'))

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('An account with this email already exists.', 'warning')
                return redirect(url_for('register'))

            initial_downloads = app.config.get('DEFAULT_FREE_DOWNLOADS', 1)
            new_user = User(
                full_name=full_name,
                email=email,
                password_hash=generate_password_hash(password),
                downloads_remaining=initial_downloads
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f'Account created successfully! You have {initial_downloads} free PDF export.', 'success')
            return redirect(url_for('dashboard'))

        return render_template('auth/register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            user = User.query.filter_by(email=email).first()
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                flash(f'Welcome back, {user.full_name}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('login'))

        return render_template('auth/login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    # --- Password Reset Flow (Resend Email Integration) ---

    def generate_reset_token(email):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        salt = app.config.get('SECURITY_PASSWORD_SALT', 'resume-portal-reset-salt')
        return serializer.dumps(email, salt=salt)

    def verify_reset_token(token, max_age=None):
        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        salt = app.config.get('SECURITY_PASSWORD_SALT', 'resume-portal-reset-salt')
        if max_age is None:
            max_age = app.config.get('RESET_TOKEN_MAX_AGE', 3600)
        try:
            return serializer.loads(token, salt=salt, max_age=max_age)
        except (SignatureExpired, BadSignature):
            return None

    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form.get('email', '').strip().lower()
            if not email:
                flash('Please enter your email address.', 'danger')
                return redirect(url_for('forgot_password'))

            user = User.query.filter_by(email=email).first()
            if user:
                token = generate_reset_token(user.email)
                reset_url = url_for('reset_password', token=token, _external=True)
                success, msg = send_password_reset_email(user.email, user.full_name, reset_url)
                if not success:
                    app.logger.warning(f"Resend delivery warning for {user.email}: {msg}")

            # Consistent feedback message to prevent account enumeration
            flash('If an account is associated with that email, password reset instructions have been sent.', 'info')
            return redirect(url_for('login'))

        return render_template('auth/forgot_password.html')

    @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        email = verify_reset_token(token)
        if not email:
            flash('The password reset link is invalid or has expired. Please request a new one.', 'danger')
            return redirect(url_for('forgot_password'))

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('Account not found.', 'danger')
            return redirect(url_for('forgot_password'))

        if request.method == 'POST':
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            if not password or len(password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('auth/reset_password.html', email=email, token=token)

            if password != confirm_password:
                flash('Passwords do not match. Please try again.', 'danger')
                return render_template('auth/reset_password.html', email=email, token=token)

            user.password_hash = generate_password_hash(password)
            db.session.commit()

            flash('Your password has been successfully reset! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))

        return render_template('auth/reset_password.html', email=email, token=token)

    # --- Dashboard & Multi-Profile Management (Phase 1) ---

    @app.route('/')
    def home():
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        profiles = ResumeProfile.query.filter_by(user_id=current_user.id)\
            .order_by(ResumeProfile.updated_at.desc()).all()
        return render_template('dashboard/index.html', profiles=profiles)

    @app.route('/profile/new', methods=['GET', 'POST'])
    @login_required
    def new_profile():
        if request.method == 'POST':
            return save_profile_data()
        return render_template('dashboard/profile_form.html', profile=None)

    @app.route('/profile/<int:profile_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_profile(profile_id):
        profile = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
        if request.method == 'POST':
            return save_profile_data(profile)
        return render_template('dashboard/profile_form.html', profile=profile)

    @app.route('/profile/<int:profile_id>/duplicate', methods=['POST'])
    @login_required
    def duplicate_profile(profile_id):
        """Allows students to quickly clone an existing profile to tailor for another role."""
        original = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()

        cloned_profile = ResumeProfile(
            user_id=current_user.id,
            profile_title=f"{original.profile_title} (Copy)",
            full_name=original.full_name,
            email=original.email,
            phone=original.phone,
            location=original.location,
            linkedin_url=original.linkedin_url,
            github_url=original.github_url,
            portfolio_url=original.portfolio_url,
            summary=original.summary,
            theme_name=original.theme_name
        )
        db.session.add(cloned_profile)
        db.session.flush()

        # Duplicate experiences
        for exp in original.experiences:
            db.session.add(Experience(
                resume_id=cloned_profile.id,
                company=exp.company,
                role=exp.role,
                duration=exp.duration,
                description=exp.description
            ))

        # Duplicate education
        for edu in original.education:
            db.session.add(Education(
                resume_id=cloned_profile.id,
                institution=edu.institution,
                degree=edu.degree,
                duration=edu.duration,
                score=edu.score
            ))

        # Duplicate skills
        for sk in original.skills:
            db.session.add(Skill(
                resume_id=cloned_profile.id,
                name=sk.name
            ))

        db.session.commit()
        flash(f'Profile duplicated! You can now customize "{cloned_profile.profile_title}".', 'success')
        return redirect(url_for('edit_profile', profile_id=cloned_profile.id))

    @app.route('/profile/<int:profile_id>/delete', methods=['POST'])
    @login_required
    def delete_profile(profile_id):
        profile = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
        db.session.delete(profile)
        db.session.commit()
        flash('Profile deleted successfully.', 'info')
        return redirect(url_for('dashboard'))

    def save_profile_data(existing_profile=None):
        profile = existing_profile or ResumeProfile(user_id=current_user.id)

        profile.profile_title = request.form.get('profile_title', '').strip() or 'My Resume'
        theme_input = request.form.get('theme_name', 'classic').strip().lower()
        profile.theme_name = theme_input if theme_input in ['classic', 'modern'] else 'classic'
        
        profile.full_name = request.form.get('full_name', '').strip()
        profile.email = request.form.get('email', '').strip()
        profile.phone = request.form.get('phone', '').strip()
        profile.location = request.form.get('location', '').strip()
        profile.linkedin_url = request.form.get('linkedin_url', '').strip()
        profile.github_url = request.form.get('github_url', '').strip()
        profile.portfolio_url = request.form.get('portfolio_url', '').strip()
        profile.summary = request.form.get('summary', '').strip()

        if not existing_profile:
            db.session.add(profile)
        db.session.flush()

        # Clear existing related collections when updating
        if existing_profile:
            Experience.query.filter_by(resume_id=profile.id).delete()
            Education.query.filter_by(resume_id=profile.id).delete()
            Skill.query.filter_by(resume_id=profile.id).delete()

        # Experiences
        companies = request.form.getlist('company[]')
        roles = request.form.getlist('role[]')
        durations = request.form.getlist('experience_duration[]')
        descriptions = request.form.getlist('description[]')

        for comp, role, dur, desc in zip(companies, roles, durations, descriptions):
            if comp.strip() or role.strip():
                db.session.add(Experience(
                    resume_id=profile.id,
                    company=comp.strip(),
                    role=role.strip(),
                    duration=dur.strip(),
                    description=desc.strip()
                ))

        # Education
        institutions = request.form.getlist('institution[]')
        degrees = request.form.getlist('degree[]')
        edu_durations = request.form.getlist('education_duration[]')
        scores = request.form.getlist('score[]')

        for inst, deg, dur, sc in zip(institutions, degrees, edu_durations, scores):
            if inst.strip() or deg.strip():
                db.session.add(Education(
                    resume_id=profile.id,
                    institution=inst.strip(),
                    degree=deg.strip(),
                    duration=dur.strip(),
                    score=sc.strip()
                ))

        # Skills (Comma-separated)
        skills_raw = request.form.get('skills', '')
        for s in skills_raw.split(','):
            cleaned = s.strip()
            if cleaned:
                db.session.add(Skill(resume_id=profile.id, name=cleaned))

        db.session.commit()
        flash('Resume profile saved successfully!', 'success')
        return redirect(url_for('dashboard'))

    # --- Resume Preview & Modular Theme Engine (Phase 2 & Phase 3) ---

    @app.route('/resume/<int:profile_id>/preview')
    @login_required
    def preview_resume(profile_id):
        profile = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()
        # Allow live theme preview switcher via query param
        theme_param = request.args.get('theme', profile.theme_name).lower()
        active_theme = theme_param if theme_param in ['classic', 'modern'] else 'classic'
        
        return render_template(
            f'resume_themes/{active_theme}.html',
            profile=profile,
            active_theme=active_theme,
            is_export_mode=False,
            auto_print=False
        )

    # --- PDF Export & Paywall Gate (Phase 4) ---

    @app.route('/resume/<int:profile_id>/export')
    @login_required
    def export_resume(profile_id):
        profile = ResumeProfile.query.filter_by(id=profile_id, user_id=current_user.id).first_or_404()

        # Paywall check
        if not current_user.is_premium and current_user.downloads_remaining <= 0:
            flash('You have used your free PDF export. Upgrade to Pro to download unlimited resumes!', 'warning')
            return redirect(url_for('checkout', needed_for=profile.id))

        # Decrement available balance if on non-premium tier
        if not current_user.is_premium:
            current_user.downloads_remaining -= 1
            db.session.commit()
            flash(f'Exported successfully! You have {current_user.downloads_remaining} free download credit(s) remaining.', 'info')

        theme_param = request.args.get('theme', profile.theme_name).lower()
        active_theme = theme_param if theme_param in ['classic', 'modern'] else 'classic'

        return render_template(
            f'resume_themes/{active_theme}.html',
            profile=profile,
            active_theme=active_theme,
            is_export_mode=True,
            auto_print=True
        )

    # --- Monetization, Checkout, and Webhook Routes (Phase 4) ---

    @app.route('/checkout')
    @login_required
    def checkout():
        return render_template('dashboard/checkout.html')

    @app.route('/pricing')
    @login_required
    def pricing():
        needed_for = request.args.get('needed_for')
        return redirect(url_for('checkout', needed_for=needed_for))

    @app.route('/checkout/upgrade', methods=['POST'])
    @login_required
    def upgrade_account():
        """Simulate instant upgrade to Pro Tier for students."""
        current_user.is_premium = True
        db.session.commit()
        flash('🎉 Congratulations! You have upgraded to Student Pro with unlimited PDF downloads.', 'success')

        needed_for = request.form.get('needed_for')
        if needed_for and needed_for.isdigit():
            return redirect(url_for('export_resume', profile_id=int(needed_for)))
        return redirect(url_for('dashboard'))

    @app.route('/checkout/add-credits', methods=['POST'])
    @login_required
    def add_credits():
        """Add 5 export credits to a free account."""
        current_user.downloads_remaining += 5
        db.session.commit()
        flash(f'Added 5 export credits! Total available: {current_user.downloads_remaining}.', 'success')

        needed_for = request.form.get('needed_for')
        if needed_for and needed_for.isdigit():
            return redirect(url_for('export_resume', profile_id=int(needed_for)))
        return redirect(url_for('dashboard'))

    @app.route('/checkout/redeem', methods=['POST'])
    @login_required
    def redeem_promo():
        """Redeem a student voucher or campus promo code."""
        code = request.form.get('promo_code', '').strip().upper()
        valid_codes = ['STUDENT100', 'UNLIMITED', 'CAMPUS2026', 'PROMO2026', 'FREEPASS']

        if code in valid_codes:
            current_user.is_premium = True
            db.session.commit()
            flash(f'Promo code "{code}" applied successfully! You now have lifetime Student Pro access.', 'success')
            needed_for = request.form.get('needed_for')
            if needed_for and needed_for.isdigit():
                return redirect(url_for('export_resume', profile_id=int(needed_for)))
            return redirect(url_for('dashboard'))
        else:
            flash(f'Invalid or expired promo code "{code}". Try code "STUDENT100".', 'danger')
            return redirect(url_for('checkout', needed_for=request.form.get('needed_for', '')))

    @app.route('/api/webhook/payment', methods=['POST'])
    def payment_webhook():
        """
        Payment webhook endpoint for automated billing updates (e.g. Stripe, Razorpay).
        Expects JSON payload with user identification and payment status.
        """
        data = request.get_json(silent=True) or {}
        event_type = data.get('event', data.get('type', 'payment.success'))
        email = data.get('email') or (data.get('data', {}).get('object', {}).get('customer_email'))
        user_id = data.get('user_id') or (data.get('data', {}).get('object', {}).get('metadata', {}).get('user_id'))

        target_user = None
        if user_id:
            target_user = db.session.get(User, int(user_id))
        elif email:
            target_user = User.query.filter_by(email=email.strip().lower()).first()

        if not target_user:
            return jsonify({'status': 'ignored', 'reason': 'User not found'}), 404

        if 'success' in event_type or 'completed' in event_type or 'paid' in event_type:
            target_user.is_premium = True
            db.session.commit()
            return jsonify({
                'status': 'success',
                'user_id': target_user.id,
                'email': target_user.email,
                'is_premium': target_user.is_premium
            }), 200

        return jsonify({'status': 'ignored', 'event': event_type}), 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
