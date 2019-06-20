from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from signal_server.api.views import DeviceView


class DeviceTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='testuser@test.com', password='12345')
        self.view = DeviceView.as_view()

    def test_device_creation(self):
        """A device can be created in the correct format"""
        request = self.factory.post('/device/', {
            'address': 'test.1',
            'identityKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'signingKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registrationId': 1234,
            'preKeys': [
                {
                    'keyId': 1,
                    'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signedPreKey': {
                'keyId': 1,
                'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['code'], 'device_created')

    def test_incorrect_device_creation(self):
        """A device cannot be created in the incorrect format"""
        request = self.factory.post('/device/', {
            'address': 'test.1',
            'identityKey': 'abcd',
            'signingKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registrationId': 1234,
            'preKeys': [
                {
                    'keyId': 1,
                    'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signedPreKey': {
                'keyId': 1,
                'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], 'invalid_data')

    def test_single_device_creation(self):
        """Creating a second device will be rejected"""
        request = self.factory.post('/device/', {
            'address': 'test.2',
            'identityKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'signingKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registrationId': 1235,
            'preKeys': [
                {
                    'keyId': 1,
                    'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signedPreKey': {
                'keyId': 1,
                'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        request = self.factory.post('/device/', {
            'address': 'test.2',
            'identityKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'signingKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registrationId': 1235,
            'preKeys': [
                {
                    'keyId': 1,
                    'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signedPreKey': {
                'keyId': 1,
                'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], 'device_exists')

    def test_device_deletion(self):
        """A device can be deleted"""
        request = self.factory.post('/device/', {
            'address': 'test.1',
            'identityKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'signingKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            'registrationId': 1234,
            'preKeys': [
                {
                    'keyId': 1,
                    'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
                }
            ],
            'signedPreKey': {
                'keyId': 1,
                'publicKey': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
                'signature': 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
            }
        }, format='json')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        request = self.factory.delete('/device/1234/')
        force_authenticate(request, user=self.user)
        response = self.view(request)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data['code'], 'device_deleted')


        