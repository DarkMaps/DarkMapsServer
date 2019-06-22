from django.test import TestCase
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate
from django.contrib.auth import get_user_model
from signal_server.api.views import UserPreKeys, Device, PreKey, SignedPreKey, Message

class PrekeysTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.factory = APIRequestFactory()
        self.client = APIClient()
        # Set up user 1
        self.user1 = User.objects.create_user(email='testuser1@test.com', password='12345')
        self.client.force_authenticate(user=self.user1)
        self.device1 = Device.objects.create(
            user = self.user1,
            address = 'test1.1',
            identityKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signingKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registrationId = 1234
        )
        PreKey.objects.create(
            device = self.device1,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device = self.device1,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        # Set up user 2
        self.user2 = User.objects.create_user(email='testuser2@test.com', password='12345')
        self.device2 = Device.objects.create(
            user = self.user2,
            address = 'test2.1',
            identityKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signingKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registrationId = 5678
        )
        PreKey.objects.create(
            device = self.device2,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device = self.device2,
            keyId = 1,
            publicKey = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature = 'abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        # Create test message from user 2 to user 1
        Message.objects.create(
            recipient = self.device1,
            content = '{"registrationId": 1234, "content": "test"}',
            senderRegistrationId = 5678,
            senderAddress = 'test2.1'
        )

    def test_send_message(self):
        """Correctly formatted messages can be sent"""
        response = self.client.post('/messages/1234/', {
            "recipient": "testuser2@test.com",
            "message": '{"registrationId": 5678, "content": "test"}'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], 2)

    def test_receive_message(self):
        """Messages can be recieved"""
        response = self.client.get('/messages/1234/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, list), True)
        self.assertEqual(response.data[0]['id'], 1)

    def test_delete_message(self):
        """Messages can be deleted"""
        response = self.client.delete('/messages/1234/', [1], format='json')
        print(response.__dict__)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, list), True)
        self.assertEqual(response.data[0], "message_deleted")