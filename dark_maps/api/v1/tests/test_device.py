"""
Tests for the device view
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient


class DeviceTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        self.user = User.objects.create_user(email='testuser@test.com', password='12345')
        self.client.force_authenticate(user=self.user)

    def test_device_creation(self):
        """A device can be created in the correct format"""
        response = self.client.post('/v1/devices/', {
            'address': 'test.1',
            'identity_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registration_id': 1234,
            'pre_keys': [
                {
                    'key_id': 1,
                    'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signed_pre_key': {
                'key_id': 1,
                'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        self.user.refresh_from_db()
        self.assertEqual(hasattr(self.user, 'device'), True)
        self.assertEqual(self.user.device.address, 'test.1')
        self.assertEqual(self.user.device.identity_key, 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(self.user.device.registration_id, 1234)
        self.assertEqual(self.user.device.prekey_set.first().key_id, 1)
        self.assertEqual(self.user.device.prekey_set.first().public_key, 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(self.user.device.signedprekey.key_id, 1)
        self.assertEqual(self.user.device.signedprekey.public_key, 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(self.user.device.signedprekey.signature, 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['code'], 'device_created')

    def test_incorrect_device_creation(self):
        """A device cannot be created in the incorrect format"""
        response = self.client.post('/v1/devices/', {
            'address': 'test.1',
            'identity_key': 'abcd',
            'registration_id': 1234,
            'pre_keys': [
                {
                    'key_id': 1,
                    'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signed_pre_key': {
                'key_id': 1,
                'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        self.user.refresh_from_db()
        self.assertEqual(hasattr(self.user, 'device'), False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'incorrect_arguments')

    def test_single_device_creation(self):
        """Creating a second device will be rejected"""
        response = self.client.post('/v1/devices/', {
            'address': 'test.1',
            'identity_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registration_id': 1235,
            'pre_keys': [
                {
                    'key_id': 1,
                    'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signed_pre_key': {
                'key_id': 1,
                'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        response = self.client.post('/v1/devices/', {
            'address': 'test.2',
            'identity_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registration_id': 1235,
            'pre_keys': [
                {
                    'key_id': 1,
                    'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signed_pre_key': {
                'key_id': 1,
                'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        self.user.refresh_from_db()
        self.assertEqual(hasattr(self.user, 'device'), True)
        self.assertEqual(self.user.device.address, 'test.1')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_exists')

    def test_device_deletion(self):
        """A device can be deleted"""
        response = self.client.post('/v1/devices/', {
            'address': 'test.1',
            'identity_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registration_id': 1234,
            'pre_keys': [
                {
                    'key_id': 1,
                    'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signed_pre_key': {
                'key_id': 1,
                'public_key': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        response = self.client.delete('/v1/devices/1234/')
        self.user.refresh_from_db()
        self.assertEqual(hasattr(self.user, 'device'), False)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data['code'], 'device_deleted')

    def test_device_put(self):
        """The /device PUT method should fail"""
        response = self.client.put('/v1/devices/', {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_device_get(self):
        """The /device GET method should fail"""
        response = self.client.get('/v1/devices/', format='json')
        self.assertEqual(response.status_code, 405)
