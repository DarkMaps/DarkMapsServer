from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from signal_server.api.views import UserPreKeys, Device, PreKey, SignedPreKey

class SignedPrekeysTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@test.com', password='12345')
        self.client.force_authenticate(user=self.user)
        device = Device.objects.create(
            user = self.user,
            address = 'test.1',
            identityKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signingKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registrationId = 1234
        )
        PreKey.objects.create(
            device = device,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device = device,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )

    def test_update_signedprekeys(self):
        """Signed prekeys on a device can be updated"""
        response = self.client.post('/signedprekey/1234/', {
                "keyId": 2,
                "publicKey": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
                "signature": 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'signed_prekey_stored')

    def test_incorrect_signedprekeys(self):
        """Signed prekeys with incorrect format cannot be created"""
        response = self.client.post('/signedprekey/1234/', {
                "keyId": 3,
                "publicKey": "abcd",
                "signature": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'invalid_data')

    def test_signedprekeys_changed_registration_id(self):
        """Signed prekeys for an incorrect identity cannot be updated"""
        response = self.client.post('/signedprekey/1235/', {
                "keyId": 2,
                "publicKey": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
                "signature": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
        }, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_changed')