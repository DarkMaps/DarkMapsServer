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
        # Set up user 1
        self.user1 = User.objects.create_user(email='testuser1@test.com', password='12345')
        self.client.force_authenticate(user=self.user1)
        self.device1 = Device.objects.create(
            user=self.user1,
            address='test1.1',
            identity_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registration_id=1234
        )
        SignedPreKey.objects.create(
            device=self.device1,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        # Set up user 2
        self.user2 = User.objects.create_user(email='testuser2@test.com', password='12345')
        self.device2 = Device.objects.create(
            user=self.user2,
            address='test2.1',
            identity_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registration_id=5678
        )
        PreKey.objects.create(
            device=self.device2,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device=self.device2,
            key_id=1,
            public_key='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        # Set up user 3
        self.user3 = User.objects.create_user(email='testuser3@test.com', password='12345')

    def test_get_prekey_bundle(self):
        """A correctly formatted prekey bundle can be obtained"""
        response = self.client.get('/v1/prekeybundles/74657374322e31/1234/', format='json')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.device.prekey_set.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual('address' in response.data, True)
        self.assertEqual('identity_key' in response.data, True)
        self.assertEqual('registration_id' in response.data, True)
        self.assertEqual('pre_key' in response.data, True)
        self.assertEqual('signed_pre_key' in response.data, True)
        self.assertEqual(response.data['address'], 'test2.1')
        self.assertEqual(response.data['identity_key'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.data['registration_id'], 5678)
        self.assertEqual(response.data['pre_key']['key_id'], 1)
        self.assertEqual(response.data['pre_key']['public_key'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.data['signed_pre_key']['key_id'], 1)
        self.assertEqual(response.data['signed_pre_key']['public_key'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.data['signed_pre_key']['signature'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')

    def test_get_prekey_bundle_no_prekeys(self):
        """When no prekeys are available a correctly formatted prekey undle can still be obtained"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/v1/prekeybundles/74657374312e31/5678/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('address' in response.data, True)
        self.assertEqual('identity_key' in response.data, True)
        self.assertEqual('registration_id' in response.data, True)
        self.assertEqual('pre_key' in response.data, False)
        self.assertEqual('signed_pre_key' in response.data, True)
        self.assertEqual(response.data['address'], 'test1.1')
        self.assertEqual(response.data['identity_key'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.data['registration_id'], 1234)
        self.assertEqual(response.data['signed_pre_key']['key_id'], 1)
        self.assertEqual(response.data['signed_pre_key']['public_key'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')
        self.assertEqual(response.data['signed_pre_key']['signature'], 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd')

    def test_get_prekey_bundle_address_not_hex(self):
        """An error is returned if the address is not provided in hex format"""
        response = self.client.get('/v1/prekeybundles/test2.1/1234/', format='json')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.device.prekey_set.count(), 1)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'incorrect_arguments')

    def test_get_prekey_bundle_no_sender_device(self):
        """When the user does not have a device to create the bundle from an error is returned"""
        self.client.force_authenticate(user=self.user3)
        response = self.client.get('/v1/prekeybundles/74657374322e31/1234/', format='json')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.device.prekey_set.count(), 1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'no_device')

    def test_get_prekey_bundle_no_recipient_device(self):
        """When the user does not have a device to create the bundle from an error is returned"""
        response = self.client.get('/v1/prekeybundles/74657374332e31/1234/', format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'no_recipient_device')

    def test_get_prekey_bundle_changed_identity(self):
        """A changed local identity results in an error"""
        response = self.client.get('/v1/prekeybundles/74657374322e31/1235/', format='json')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.device.prekey_set.count(), 1)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_changed')

    def test_put_prekey_bundle(self):
        """The /prekeybundle PUT method should fail"""
        response = self.client.put('/v1/prekeybundles/74657374322e31/1235/', {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_post_prekey_bundle(self):
        """The /prekeybundle POST method should fail"""
        response = self.client.post('/v1/prekeybundles/74657374322e31/1235/', {}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_delete_prekey_bundle(self):
        """The /prekeybundle POST method should fail"""
        response = self.client.delete('/v1/prekeybundles/74657374322e31/1235/', format='json')
        self.assertEqual(response.status_code, 405)
