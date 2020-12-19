"""
Tests for the prekey view
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from signal_server.api.v1.models import Device, PreKey, SignedPreKey

class PrekeysTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@test.com', password='12345')
        self.user2 = User.objects.create_user(email='testusertest@test.com', password='12345')
        self.client.force_authenticate(user=self.user)
        self.device = Device.objects.create(
            user=self.user,
            address='test.1',
            identity_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registration_id=1234
        )
        PreKey.objects.create(
            device=self.device,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device=self.device,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )

    def test_update_prekeys(self):
        """Prekeys on a device can be updated"""
        response = self.client.post('/v1/1234/prekeys/', [
            {
                "key_id": 2,
                "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
            }
        ], format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.prekey_set.count(), 2)
        self.assertEqual(self.user.device.prekey_set.all()[1].key_id, 2)
        self.assertEqual(self.user.device.prekey_set.all()[1].public_key, "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 'prekeys_stored')

    def test_duplicate_prekeys(self):
        """Prekeys with a duplicate keyID cannot be created"""
        response = self.client.post('/v1/1234/prekeys/', [
            {
                "key_id": 1,
                "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd"
            }
        ], format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.prekey_set.count(), 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'prekey_id_exists')

    def test_incorrect_prekeys(self):
        """Prekeys with incorrect format cannot be created"""
        response = self.client.post('/v1/1234/prekeys/', [
            {
                "key_id": 3,
                "public_key": "abcd"
            }
        ], format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.prekey_set.count(), 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'incorrect_arguments')

    def test_prekeys_changed_registration_id(self):
        """Prekeys for an incorrect identity cannot be updated"""
        response = self.client.post('/v1/1235/prekeys/', [
            {
                "key_id": 3,
                "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            }
        ], format='json')
        self.user.refresh_from_db()
        self.assertEqual(self.user.device.prekey_set.count(), 1)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_changed')

    def test_update_prekeys_no_device(self):
        """Prekeys for an incorrect identity cannot be updated"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.post('/v1/1234/prekeys/', [
            {
                "key_id": 2,
                "public_key": "abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd",
            }
        ], format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'no_device')

    def test_prekeys_get(self):
        """The /prekeys GET method should do nothing"""
        response = self.client.get('/v1/1234/prekeys/', format='json')
        self.assertEqual(response.status_code, 405)

    def test_prekeys_put(self):
        """The /prekeys PUT method should do nothing"""
        response = self.client.put('/v1/1234/prekeys/', {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_prekeys_delete(self):
        """The /prekeys DELETE method should do nothing"""
        response = self.client.delete('/v1/1234/prekeys/', format='json')
        self.assertEqual(response.status_code, 405)
