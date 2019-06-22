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
        self.device = Device.objects.create(
            user = self.user,
            address = 'test.1',
            identityKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signingKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registrationId = 1234
        )
        PreKey.objects.create(
            device = self.device,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device = self.device,
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
        self.assertEqual(response.data['code'], 'prekey_id_exists')

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

    def test_prekeys_changed_registration_id(self):
        """Prekeys for an incorrect identity cannot be updated"""
        response = self.client.post('/prekeys/1235/', [
            {
                "keyId": 3,
                "publicKey": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            }
        ], format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_changed')

    # TODO: Fix
    def test_update_prekeys_no_device(self):
        """Prekeys for an incorrect identity cannot be updated"""
        # Have to create new user, as unable to correctly test deleting device of previous user
        User = get_user_model()
        self.user2 = User.objects.create_user(email='testusertest@test.com', password='12345')
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/prekeys/1234/', [
            {
                "keyId": 2,
                "publicKey": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            }
        ], format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'no_device')