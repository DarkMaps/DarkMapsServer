"""
Tests for the signed prekey view
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from dark_maps.api.v1.models import Device, PreKey, SignedPreKey

class SignedPrekeysTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@test.com', password='12345')
        self.user2 = User.objects.create_user(email='testusertest@test.com', password='12345')
        self.client.force_authenticate(user=self.user)
        device = Device.objects.create(
            user=self.user,
            address='test.1',
            identity_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registration_id=1234
        )
        PreKey.objects.create(
            device=device,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device=device,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )

    def test_update_signedprekeys(self):
        """Signed prekeys on a device can be updated"""
        response = self.client.post('/v1/1234/signedprekeys/', {
            "key_id": 2,
            "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "signature": 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        }, format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.signedprekey.key_id, 2)
        self.assertEqual(self.user.device.signedprekey.public_key, 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(self.user.device.signedprekey.signature, 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'signed_prekey_stored')

    def test_incorrect_signedprekeys(self):
        """Signed prekeys with incorrect format cannot be created"""
        response = self.client.post('/v1/1234/signedprekeys/', {
            "key_id": 3,
            "public_key": "abcd",
            "signature": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
        }, format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.signedprekey.key_id, 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'incorrect_arguments')

    def test_signedprekeys_changed_registration_id(self):
        """Signed prekeys for an incorrect identity cannot be updated"""
        response = self.client.post('/v1/1235/signedprekeys/', {
            "key_id": 2,
            "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "signature": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
        }, format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.signedprekey.key_id, 1)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_changed')

    def test_signedprekeys_no_device(self):
        """Signed prekeys provided for a user with no device should fail"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/v1/1235/signedprekeys/', {
            "key_id": 2,
            "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            "signature": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
        }, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'no_device')

    def test_signedprekeys_get(self):
        """The /signedprekeys GET method should do nothing"""
        response = self.client.get('/v1/1234/signedprekeys/', format='json')
        self.assertEqual(response.status_code, 405)

    def test_signedprekeys_put(self):
        """The /signedprekeys PUT method should do nothing"""
        response = self.client.put('/v1/1234/signedprekeys/', {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_signedprekeys_delete(self):
        """The /signedprekeys DELETE method should do nothing"""
        response = self.client.delete('/v1/1234/signedprekeys/', format='json')
        self.assertEqual(response.status_code, 405)
