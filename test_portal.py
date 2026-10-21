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


if __name__ == '__main__':
    unittest.main()
