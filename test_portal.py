import unittest
from app import create_app
from models import db, User, ResumeProfile, Experience, Education, Skill

class ResumePortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def register_and_login(self, email="student@university.edu", password="securepassword", name="Alex Student"):
        # Register
        res = self.client.post('/register', data={
            'full_name': name,
            'email': email,
            'password': password
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        return email

    def test_auth_flow(self):
        """Phase 1: Test user registration, login and logout."""
        email = self.register_and_login()
        user = User.query.filter_by(email=email).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.full_name, "Alex Student")
        self.assertEqual(user.downloads_remaining, 1)
        self.assertFalse(user.is_premium)

        # Logout
        res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out', res.data)

        # Login
        res = self.client.post('/login', data={
            'email': email,
            'password': 'securepassword'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back', res.data)

    def test_resume_crud_and_duplicate(self):
        """Phase 1: Create, Edit, Duplicate, and Delete resume profiles."""
        self.register_and_login()
        user = User.query.first()

        # Create new profile
        res = self.client.post('/profile/new', data={
            'profile_title': 'Frontend Developer',
            'theme_name': 'modern',
            'full_name': 'Alex Student',
            'email': 'alex@example.com',
            'phone': '+1 555 123 4567',
            'location': 'New York, NY',
            'linkedin_url': 'https://linkedin.com/in/alexstudent',
            'github_url': 'https://github.com/alexstudent',
            'portfolio_url': 'https://alexstudent.dev',
            'summary': 'Passionate frontend developer skilled in React and UI design.',
            'skills': 'JavaScript, React, CSS, Git, HTML5',
            'company[]': ['Tech Corp', 'Design Studio'],
            'role[]': ['Frontend Intern', 'Web Designer'],
            'experience_duration[]': ['Summer 2024', 'Fall 2023'],
            'description[]': ['Built responsive web apps\nImproved loading performance', 'Designed prototypes'],
            'institution[]': ['NYU'],
            'degree[]': ['B.S. Computer Science'],
            'education_duration[]': ['2021 - 2025'],
            'score[]': ['3.9 GPA']
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        profile = ResumeProfile.query.filter_by(user_id=user.id).first()
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profile_title, 'Frontend Developer')
        self.assertEqual(profile.theme_name, 'modern')
        self.assertEqual(len(profile.experiences), 2)
        self.assertEqual(len(profile.education), 1)
        self.assertEqual(len(profile.skills), 5)

        # Duplicate profile (cloning for another role)
        res_dup = self.client.post(f'/profile/{profile.id}/duplicate', follow_redirects=True)
        self.assertEqual(res_dup.status_code, 200)
        
        all_profiles = ResumeProfile.query.filter_by(user_id=user.id).all()
        self.assertEqual(len(all_profiles), 2)
        dup = [p for p in all_profiles if '(Copy)' in p.profile_title][0]
        self.assertEqual(len(dup.experiences), 2)
        self.assertEqual(len(dup.skills), 5)

        # Delete profile
        res_del = self.client.post(f'/profile/{dup.id}/delete', follow_redirects=True)
        self.assertEqual(res_del.status_code, 200)
        self.assertIsNone(db.session.get(ResumeProfile, dup.id))

    def test_theme_preview_classic_and_modern(self):
        """Phase 2 & 3: Test resume rendering in Classic and Modern themes."""
        self.register_and_login()
        user = User.query.first()

        profile = ResumeProfile(
            user_id=user.id,
            profile_title='Backend Engineer',
            theme_name='classic',
            full_name='Jordan Lee',
            email='jordan@university.edu',
            location='Austin, TX',
            summary='Python and Flask developer.'
        )
        db.session.add(profile)
        db.session.flush()

        db.session.add(Experience(resume_id=profile.id, company='Cloud Co', role='Cloud Intern', duration='2024', description='API development'))
        db.session.add(Education(resume_id=profile.id, institution='UT Austin', degree='B.S. ECE', duration='2024', score='3.8 GPA'))
        db.session.add(Skill(resume_id=profile.id, name='Python'))
        db.session.add(Skill(resume_id=profile.id, name='Flask'))
        db.session.commit()

        # Preview Classic theme
        res_classic = self.client.get(f'/resume/{profile.id}/preview?theme=classic')
        self.assertEqual(res_classic.status_code, 200)
        self.assertIn(b'classic.css', res_classic.data)
        self.assertIn(b'Jordan Lee', res_classic.data)
        self.assertIn(b'Cloud Co', res_classic.data)

        # Preview Modern theme
        res_modern = self.client.get(f'/resume/{profile.id}/preview?theme=modern')
        self.assertEqual(res_modern.status_code, 200)
        self.assertIn(b'modern.css', res_modern.data)
        self.assertIn(b'Jordan Lee', res_modern.data)
        self.assertIn(b'Cloud Co', res_modern.data)

    def test_paywall_and_monetization_flow(self):
        """Phase 4: Test PDF download limit, Paywall Gate, and Promo/Upgrade unlocks."""
        self.register_and_login()
        user = User.query.first()
        self.assertEqual(user.downloads_remaining, 1)
        self.assertFalse(user.is_premium)

        profile = ResumeProfile(
            user_id=user.id,
            profile_title='Data Analyst',
            full_name='Sam Smith',
            email='sam@analyst.edu'
        )
        db.session.add(profile)
        db.session.commit()

        # 1st Export: Should succeed and decrement remaining downloads from 1 to 0
        res_exp1 = self.client.get(f'/resume/{profile.id}/export')
        self.assertEqual(res_exp1.status_code, 200)
        self.assertIn(b'data-auto-print="true"', res_exp1.data)
        
        user_after = db.session.get(User, user.id)
        self.assertEqual(user_after.downloads_remaining, 0)

        # 2nd Export: Should hit Paywall gate and redirect to /checkout
        res_exp2 = self.client.get(f'/resume/{profile.id}/export')
        self.assertEqual(res_exp2.status_code, 302)
        self.assertIn('/checkout', res_exp2.headers['Location'])

        # Visit checkout page
        res_checkout = self.client.get('/checkout')
        self.assertEqual(res_checkout.status_code, 200)
        self.assertIn(b'Student Pro Pass', res_checkout.data)

        # Redeem promo code STUDENT100
        res_redeem = self.client.post('/checkout/redeem', data={
            'promo_code': 'STUDENT100'
        }, follow_redirects=True)
        self.assertEqual(res_redeem.status_code, 200)

        user_pro = db.session.get(User, user.id)
        self.assertTrue(user_pro.is_premium)

        # 3rd Export: Now allowed because user is Premium!
        res_exp3 = self.client.get(f'/resume/{profile.id}/export')
        self.assertEqual(res_exp3.status_code, 200)
        self.assertIn(b'data-auto-print="true"', res_exp3.data)

    def test_payment_webhook(self):
        """Phase 4: Webhook integration endpoint for Stripe / Razorpay payments."""
        self.register_and_login(email="paying_student@university.edu")
        user = User.query.filter_by(email="paying_student@university.edu").first()
        self.assertFalse(user.is_premium)

        # Send webhook event
        res = self.client.post('/api/webhook/payment', json={
            'event': 'checkout.session.completed',
            'email': user.email
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')

        updated_user = db.session.get(User, user.id)
        self.assertTrue(updated_user.is_premium)

    def test_render_postgresql_uri_normalization(self):
        """Test PostgreSQL integration & Render URI normalization (postgres:// to postgresql://)."""
        import os
        from config import get_database_uri

        # Test Render's postgres:// prefix
        old_env = os.environ.get('DATABASE_URL')
        try:
            os.environ['DATABASE_URL'] = 'postgres://user:pass@dpg-xxx.render.com:5432/db_name'
            self.assertEqual(get_database_uri(), 'postgresql://user:pass@dpg-xxx.render.com:5432/db_name')

            # Test standard postgresql://
            os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost:5432/db_name'
            self.assertEqual(get_database_uri(), 'postgresql://user:pass@localhost:5432/db_name')
        finally:
            if old_env is not None:
                os.environ['DATABASE_URL'] = old_env
            else:
                os.environ.pop('DATABASE_URL', None)

    def test_forgot_and_reset_password_flow(self):
        """Test complete Forgot Password and Reset Password flow with token validation."""
        email = self.register_and_login(email="forgot_student@university.edu", password="old_password123", name="Reset Tester")
        self.client.get('/logout')

        # 1. Login page should have 'Forgot password?' option and embedded reset form
        res_login = self.client.get('/login')
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Forgot password?', res_login.data)
        self.assertIn(b'/forgot-password', res_login.data)
        self.assertIn(b'forgot-panel', res_login.data)
        self.assertIn(b'Send Reset Link', res_login.data)

        # 2. Visit Forgot Password page
        res_forgot_page = self.client.get('/forgot-password')
        self.assertEqual(res_forgot_page.status_code, 200)
        self.assertIn(b'Reset Password', res_forgot_page.data)

        # 3. Submit Forgot Password form
        res_submit_forgot = self.client.post('/forgot-password', data={
            'email': email
        }, follow_redirects=True)
        self.assertEqual(res_submit_forgot.status_code, 200)
        self.assertIn(b'password reset instructions have been sent', res_submit_forgot.data)

        # 4. Generate a valid token for this user
        from itsdangerous import URLSafeTimedSerializer
        serializer = URLSafeTimedSerializer(self.app.config['SECRET_KEY'])
        salt = self.app.config.get('SECURITY_PASSWORD_SALT', 'resume-portal-reset-salt')
        valid_token = serializer.dumps(email, salt=salt)

        # 5. Access Reset Password page with valid token
        res_reset_page = self.client.get(f'/reset-password/{valid_token}')
        self.assertEqual(res_reset_page.status_code, 200)
        self.assertIn(b'Set New Password', res_reset_page.data)
        self.assertIn(b'forgot_student@university.edu', res_reset_page.data)

        # 6. Access Reset Password with invalid token -> should redirect
        res_invalid = self.client.get('/reset-password/totally-fake-token-12345', follow_redirects=True)
        self.assertEqual(res_invalid.status_code, 200)
        self.assertIn(b'invalid or has expired', res_invalid.data)

        # 7. Submit mismatched passwords -> should fail
        res_mismatch = self.client.post(f'/reset-password/{valid_token}', data={
            'password': 'new_secure_password',
            'confirm_password': 'wrong_password'
        })
        self.assertEqual(res_mismatch.status_code, 200)
        self.assertIn(b'Passwords do not match', res_mismatch.data)

        # 8. Submit matching valid new password -> should succeed
        res_reset_success = self.client.post(f'/reset-password/{valid_token}', data={
            'password': 'new_secure_password',
            'confirm_password': 'new_secure_password'
        }, follow_redirects=True)
        self.assertEqual(res_reset_success.status_code, 200)
        self.assertIn(b'Your password has been successfully reset', res_reset_success.data)

        # 9. Verify user cannot login with old password
        res_old_login = self.client.post('/login', data={
            'email': email,
            'password': 'old_password123'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', res_old_login.data)

        # 10. Verify user CAN login with NEW password
        res_new_login = self.client.post('/login', data={
            'email': email,
            'password': 'new_secure_password'
        }, follow_redirects=True)
        self.assertIn(b'Welcome back', res_new_login.data)
        self.assertIn(b'Reset Tester', res_new_login.data)

    def test_email_service_providers(self):
        """Test Resend, ZeptoMail, and SMTP email dispatch helpers."""
        from email_service import build_reset_email_html, send_password_reset_email
        html = build_reset_email_html("Alex Tester", "https://example.com/reset/token123")
        self.assertIn("Alex Tester", html)
        self.assertIn("https://example.com/reset/token123", html)
        self.assertIn("ResumePortal", html)

        # 1. Test Resend provider (Default)
        self.app.config['EMAIL_PROVIDER'] = 'resend'
        success_resend, _ = send_password_reset_email("test_resend@example.com", "Alex Resend", "https://example.com/reset/token123")
        self.assertTrue(success_resend)

        # 2. Test ZeptoMail provider
        self.app.config['EMAIL_PROVIDER'] = 'zeptomail'
        success_zepto, _ = send_password_reset_email("test_zepto@example.com", "Alex Zepto", "https://example.com/reset/token456")
        self.assertTrue(success_zepto)

        # 3. Test SMTP provider
        self.app.config['EMAIL_PROVIDER'] = 'smtp'
        success_smtp, _ = send_password_reset_email("test_smtp@example.com", "Alex SMTP", "https://example.com/reset/token789")
        self.assertTrue(success_smtp)

        # Reset to default
        self.app.config['EMAIL_PROVIDER'] = 'resend'

    def test_root_opens_login_page_even_when_authenticated(self):
        """Test that root URL (/) directs to login and /login renders without bouncing to dashboard."""
        # 1. Unauthenticated visit to root / redirects to /login
        res_root = self.client.get('/')
        self.assertEqual(res_root.status_code, 302)
        self.assertIn('/login', res_root.headers['Location'])

        # 2. Unauthenticated visit to /login returns 200 with login form
        res_login = self.client.get('/login')
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b'Welcome Back', res_login.data)
        self.assertIn(b'Forgot password?', res_login.data)

        # 3. Log in a user
        self.register_and_login(email="active_user@university.edu", name="Active User")

        # 4. Even when authenticated, root / directs to /login (allowing user to see login page)
        res_root_auth = self.client.get('/')
        self.assertEqual(res_root_auth.status_code, 302)
        self.assertIn('/login', res_root_auth.headers['Location'])

        # 5. /login renders 200 without auto-bouncing to dashboard, showing active session banner
        res_login_auth = self.client.get('/login')
        self.assertEqual(res_login_auth.status_code, 200)
        self.assertIn(b'Welcome Back', res_login_auth.data)
        self.assertIn(b'Currently signed in as', res_login_auth.data)
        self.assertIn(b'Active User', res_login_auth.data)
        self.assertIn(b'Go to Dashboard', res_login_auth.data)

        # 6. Unauthenticated attempt to visit /dashboard directly is still protected by @login_required
        self.client.get('/logout')
        res_dash = self.client.get('/dashboard')
        self.assertEqual(res_dash.status_code, 302)
        self.assertIn('/login', res_dash.headers['Location'])


if __name__ == '__main__':
    unittest.main()
