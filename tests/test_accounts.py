"""
Unit tests for accounts app.
Tests: Registration, Login, Password Reset
"""

from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, EmailVerification


class RegistrationTest(TestCase):
    """US-01: ثبت‌نام"""

    def test_register_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_success(self):
        data = {
            'first_name': 'علی', 'last_name': 'محمدی',
            'role': 'student', 'student_id': '40012345678',
            'email': 'ali@test.com', 'phone': '09123456789',
            'password': 'StrongPass123!', 'password_confirm': 'StrongPass123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(student_id='40012345678').exists())

    def test_register_duplicate_email(self):
        User.objects.create_user(student_id='111', email='dup@test.com', password='pass1234')
        data = {
            'first_name': 'تست', 'last_name': 'تست',
            'role': 'student', 'student_id': '222',
            'email': 'dup@test.com', 'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)  # stays on page with error

    def test_register_password_mismatch(self):
        data = {
            'first_name': 'تست', 'last_name': 'تست',
            'role': 'student', 'student_id': '333',
            'email': 'test3@test.com', 'password': 'StrongPass123!',
            'password_confirm': 'DifferentPass!',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)

    def test_register_short_password(self):
        data = {
            'first_name': 'تست', 'last_name': 'تست',
            'role': 'student', 'student_id': '444',
            'email': 'test4@test.com', 'password': '123',
            'password_confirm': '123',
        }
        response = self.client.post(reverse('accounts:register'), data)
        self.assertEqual(response.status_code, 200)


class LoginTest(TestCase):
    """US-02: ورود"""

    def setUp(self):
        self.user = User.objects.create_user(
            student_id='40012345678', email='test@test.com',
            password='TestPass123!', first_name='تست', last_name='تست',
            is_verified=True
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        data = {'student_id': '40012345678', 'password': 'TestPass123!'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)

    def test_login_wrong_password(self):
        data = {'student_id': '40012345678', 'password': 'WrongPass!'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)

    def test_login_nonexistent_user(self):
        data = {'student_id': '99999999', 'password': 'TestPass123!'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 200)

    def test_login_unverified_user(self):
        self.user.is_verified = False
        self.user.save()
        data = {'student_id': '40012345678', 'password': 'TestPass123!'}
        response = self.client.post(reverse('accounts:login'), data)
        self.assertEqual(response.status_code, 302)  # redirects to verify


class PasswordResetTest(TestCase):
    """US-03: بازیابی رمز"""

    def setUp(self):
        self.user = User.objects.create_user(
            student_id='40012345678', email='test@test.com',
            password='TestPass123!', first_name='تست', last_name='تست',
            is_verified=True
        )

    def test_reset_page_loads(self):
        response = self.client.get(reverse('accounts:password_reset'))
        self.assertEqual(response.status_code, 200)

    def test_reset_request_with_email(self):
        response = self.client.post(reverse('accounts:password_reset'), {'identifier': 'test@test.com'})
        self.assertEqual(response.status_code, 302)

    def test_reset_request_with_student_id(self):
        response = self.client.post(reverse('accounts:password_reset'), {'identifier': '40012345678'})
        self.assertEqual(response.status_code, 302)

    def test_reset_nonexistent_user(self):
        response = self.client.post(reverse('accounts:password_reset'), {'identifier': 'nobody@test.com'})
        self.assertEqual(response.status_code, 200)


class UserModelTest(TestCase):
    """تست مدل User"""

    def test_create_user(self):
        user = User.objects.create_user(
            student_id='123', email='u@t.com', password='pass1234',
            first_name='نام', last_name='فامیل'
        )
        self.assertEqual(user.full_name, 'نام فامیل')
        self.assertFalse(user.is_verified)
        self.assertTrue(user.check_password('pass1234'))

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            student_id='admin1', email='admin@t.com', password='admin1234',
            first_name='مدیر', last_name='سیستم'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_admin_user)

    def test_role_properties(self):
        student = User(role='student')
        tech = User(role='technician')
        admin = User(role='admin')
        self.assertTrue(student.is_reporter)
        self.assertTrue(tech.is_technician)
        self.assertTrue(admin.is_admin_user)
