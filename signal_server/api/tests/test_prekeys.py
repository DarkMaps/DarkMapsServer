from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from signal_server.api.views import UserPreKeys, Device, PreKey, SignedPreKey

class PrekeysTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@test.com', password='12345')
        self.client.force_authenticate(user=self.user)
        self.view = UserPreKeys.as_view()
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

    def test_update_prekeys(self):
        """Prekeys on a device can be updated"""
        response = self.client.post('/prekeys/1234/', [
            {
                "keyId": 2,
                "publicKey": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
            }
        ], format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'prekeys_stored')

    def test_duplicate_prekeys(self):
        """Prekeys with a duplicate keyID cannot be created"""
        response = self.client.post('/prekeys/1234/', [
            {
                "keyId": 1,
                "publicKey": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
            }
        ], format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'invalid_data')

    def test_incorrect_prekeys(self):
        """Prekeys with incorrect format cannot be created"""
        response = self.client.post('/prekeys/1234/', [
            {
                "keyId": 3,
                "publicKey": "abcd"
            }
        ], format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'invalid_data')