from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIClient, force_authenticate
from django.contrib.auth import get_user_model
from signal_server.api.views import DeviceView
from trench.utils import create_otp_code


class DeviceTestCase(TestCase):
    def setUp(self):
        self.UserModel = get_user_model()
        self.client = APIClient()
        self.client.credentials()
        self.user = self.UserModel.objects.create_user(email='testuser@test.com', password=12345)


    def test_sign_up(self):
        """A user can sign up without 2fa"""
        response = self.client.post('/auth/users/', {
            "email": "test@test.com",
            "password": "testpassword"
        })
        self.assertEqual(self.UserModel.objects.count(), 2)
        user = self.UserModel.objects.get(id = 2)
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "test@test.com")
        self.assertEqual(response.data["id"], 2)

    def test_log_in_no_2fa(self):
        """User can login when 2fa not active and authorised call succeeds"""
        response = self.client.post('/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("auth_token" in response.data, True)
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.get('/auth/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], 'testuser@test.com')

    def test_log_in_no_2fa(self):
        """User can log in when 2fa not active and authorised call succeeds"""
        response = self.client.post('/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("auth_token" in response.data, True)
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.get('/auth/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], 'testuser@test.com')

    def test_log_out(self):
        """User can log out"""
        response = self.client.post('/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.post('/auth/logout/')
        self.assertEqual(response.status_code, 204)

    def test_2fa_activate(self):
        """User can activate 2fa"""
        # Login
        response = self.client.post('/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        # Activate a method
        response = self.client.post("/auth/email/activate/", {})
        self.assertEqual(response.status_code, 200)
        MFAMethod = apps.get_model('trench.MFAMethod')
        MFA = MFAMethod.objects.get(user=self.user, name='email')
        code = create_otp_code(MFA.secret)
        response = self.client.post('/auth/email/activate/confirm/', {
            "code": code})
        self.assertEqual(response.status_code, 200)

    def test_2fa_login_with_2fa(self):

    def test_2fa_disable_2fa(self):
        
    def test_user_delete(self):

    def test_djoser_token_login_fail(self):

    def test_djoser_jwt_login_fail(self):