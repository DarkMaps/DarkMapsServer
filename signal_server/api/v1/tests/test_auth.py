import json, base64
import nacl
from urllib.parse import quote

from django.test import TestCase
from django.apps import apps
from rest_framework.test import APIClient, force_authenticate
from django.contrib.auth import get_user_model
from signal_server.api.v1.views import DeviceView
from trench.utils import create_otp_code, create_secret
from signal_server.api.v1.views import Device, PreKey, SignedPreKey


class DeviceTestCase(TestCase):
    def setUp(self):
        self.UserModel = get_user_model()
        self.client = APIClient()
        self.client.credentials()
        self.user = self.UserModel.objects.create_user(email='testuser@test.com', password=12345)
        self.user2 = self.UserModel.objects.create_user(email='testuser2@test.com', password=12345)
        MFAMethod = apps.get_model('trench.MFAMethod')
        MFAMethod.objects.create(
            user=self.user2,
            secret=create_secret(),
            is_primary=True,
            name='email',
            is_active=True,
        )
        self.user3 = self.UserModel.objects.create_user(email='testuser3@test.com', password=12345)
        self.device3 = Device.objects.create(
            user = self.user3,
            address = 'test3.1',
            identityKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signingKey = '+VelPrSGylnf3KBmyRHfFt0NnV6zRIDmpCpE5/dtHy4=',
            registrationId = 1234,
            signatureCount = 0
        )
        PreKey.objects.create(
            device = self.device3,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device = self.device3,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )


    def test_sign_up(self):
        """A user can sign up without 2fa"""
        response = self.client.post('/v1/auth/users/', {
            "email": "test@test.com",
            "password": "testpassword"
        })
        self.assertEqual(self.UserModel.objects.count(), 4)
        user = self.UserModel.objects.get(id = 4)
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], "test@test.com")
        self.assertEqual(response.data["id"], 4)

    def test_log_in_no_2fa(self):
        """User can log in when 2fa not active and authorised call succeeds"""
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("auth_token" in response.data, True)
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.get('/v1/auth/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], 'testuser@test.com')

    def test_log_out(self):
        """User can log out"""
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.post('/v1/auth/logout/')
        self.assertEqual(response.status_code, 204)

    def test_2fa_activate(self):
        """User can activate 2fa"""
        # Login
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        # Activate a method
        response = self.client.post("/v1/auth/email/activate/", {})
        self.assertEqual(response.status_code, 200)
        # Create a code
        MFAMethod = apps.get_model('trench.MFAMethod')
        MFA = MFAMethod.objects.get(user=self.user, name='email')
        code = create_otp_code(MFA.secret)
        # Confirm the method
        response = self.client.post('/v1/auth/email/activate/confirm/', {
            "code": code})
        self.assertEqual(response.status_code, 200)

    def test_2fa_login_with_2fa(self):
        """User can log in when 2fa is active and authorised call succeeds"""
        # Get ephemeral token
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser2@test.com', 
            "password": 12345})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("ephemeral_token" in response.data, True)
        # Create a code
        MFAMethod = apps.get_model('trench.MFAMethod')
        MFA = MFAMethod.objects.get(user=self.user2, name='email')
        code = create_otp_code(MFA.secret)
        # 2FA Login
        response = self.client.post('/v1/auth/login/code/', {
            "ephemeral_token": response.data['ephemeral_token'], 
            "code": code})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("auth_token" in response.data, True)
        # Check authorised call
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.get('/v1/auth/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], 'testuser2@test.com')

    def test_2fa_disable_2fa(self):
        """User can disable a 2fa method"""
        # Get ephemeral token
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser2@test.com', 
            "password": 12345})
        # Create a code
        MFAMethod = apps.get_model('trench.MFAMethod')
        MFA = MFAMethod.objects.get(user=self.user2, name='email')
        code = create_otp_code(MFA.secret)
        # 2FA Login
        response = self.client.post('/v1/auth/login/code/', {
            "ephemeral_token": response.data['ephemeral_token'], 
            "code": code})
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        # Test disable
        response = self.client.post('/v1/auth/email/deactivate/', {
            "code": code
        })
        self.assertEqual(response.status_code, 204)
        
    def test_user_delete(self):
        """User can delete their record"""
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.client.credentials(HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        response = self.client.delete('/v1/auth/users/me/', {
            "currentPassword": 12345})
        self.assertEqual(response.status_code, 204)

    def test_djoser_token_login_fail(self):
        """The usual djoser token login fails (cannot avoid 2fa)"""
        response = self.client.post('/v1/auth/token/login/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.assertEqual(response.status_code, 404)

    def test_djoser_jwt_login_fail(self):
        """The usual djoser jwt login fails (cannot avoid 2fa)"""
        response = self.client.post('/v1/auth/jwt/create/', {
            "email": 'testuser@test.com', 
            "password": 12345})
        self.assertEqual(response.status_code, 404)

    def test_request_signing(self):
        """Properly signed requests will succeed"""
        # Login
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser3@test.com', 
            "password": 12345})
        # Create signing details
        privateKey = 'oPHKPY0XHkzxWn2dqB9UGRaAVlWlprrtRrD+rkGI3CE='
        signatureCount = 0
        encodedUrl = quote('/v1/prekeys/1234/'.encode("utf-8"), safe='')
        postData = json.dumps(
            [{"keyId": 2, "publicKey": 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'}],
            ensure_ascii=False, indent=None, separators=(',', ':')
        )
        postData = quote(postData.encode("utf-8"), safe='()!*\'')
        signingMessage = str(signatureCount) + encodedUrl + postData
        # NB: In the python library you instantiate the signer with a seed, not the private key, hence lengths are different
        signingKey = nacl.signing.SigningKey(base64.b64decode(privateKey))
        signedMessage = signingKey.sign(str.encode(signingMessage))
        signedMessage = base64.b64encode(signedMessage.signature).decode('UTF-8')
        self.client.credentials(HTTP_SIGNATURE=signedMessage, HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        # Test a response
        response = self.client.post('/v1/prekeys/1234/', 
            json.dumps([{"keyId": 2, "publicKey": 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'}]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'prekeys_stored')



    def test_request_signing_incorrect(self):
        """Improperly signed requests will fail"""
        # Login
        response = self.client.post('/v1/auth/login/', {
            "email": 'testuser3@test.com', 
            "password": 12345})
        # Create signing details
        privateKey = 'oPHKPY0XHkzxWn2dqB9UGRaAVlWlprrtRrD+rkGI3CE='
        # NOTE: Deliberately incorrect counter
        signatureCount = 100
        encodedUrl = quote('/prekeys/1234/'.encode("utf-8"), safe='')
        postData = json.dumps(
            [{"keyId": 2, "publicKey": 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'}],
            ensure_ascii=False, indent=None, separators=(',', ':')
        )
        postData = quote(postData.encode("utf-8"), safe='()!*\'')
        signingMessage = str(signatureCount) + encodedUrl + postData
        # NB: In the python library you instantiate the signer with a seed, not the private key, hence lengths are different
        signingKey = nacl.signing.SigningKey(base64.b64decode(privateKey))
        signedMessage = signingKey.sign(str.encode(signingMessage))
        signedMessage = base64.b64encode(signedMessage.signature).decode('UTF-8')
        self.client.credentials(HTTP_SIGNATURE=signedMessage, HTTP_AUTHORIZATION="Token "+response.data["auth_token"])
        # Test a response
        response = self.client.post('/v1/prekeys/1234/', 
            json.dumps([{"keyId": 2, "publicKey": 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'}]),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')