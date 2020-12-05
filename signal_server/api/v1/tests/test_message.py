"""
Tests for the message view
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from signal_server.api.v1.models import Device, PreKey, SignedPreKey, Message

class MessageTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.client = APIClient()
        # Set up user 1
        self.user1 = User.objects.create_user(email='testuser1@test.com', password='12345')
        self.client.force_authenticate(user=self.user1)
        self.device1 = Device.objects.create(
            user=self.user1,
            address='test1.1',
            identityKey='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registrationId=1234
        )
        PreKey.objects.create(
            device=self.device1,
            keyId=1,
            publicKey='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device=self.device1,
            keyId=1,
            publicKey='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        # Set up user 2
        self.user2 = User.objects.create_user(email='testuser2@test.com', password='12345')
        self.device2 = Device.objects.create(
            user=self.user2,
            address='test2.1',
            identityKey='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            registrationId=5678
        )
        PreKey.objects.create(
            device=self.device2,
            keyId=1,
            publicKey='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        SignedPreKey.objects.create(
            device=self.device2,
            keyId=1,
            publicKey='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd',
            signature='abcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcdabcd'
        )
        # Create test message from user 2 to user 1
        Message.objects.create(
            recipient=self.device1,
            content='{"registrationId": 1234, "content": "test"}',
            senderRegistrationId=5678,
            senderAddress='test2.1'
        )

    def test_send_message(self):
        """Correctly formatted messages can be sent"""
        response = self.client.post('/v1/1234/messages/', {
            "recipient": "testuser2@test.com",
            "message": '{"registrationId": 5678, "content": "test"}'
        }, format='json')
        self.user1.refresh_from_db()
        self.assertEqual(hasattr(self.user2.device, 'received_messages'), True)
        self.assertEqual(self.user2.device.received_messages.count(), 1)
        self.assertEqual(self.user2.device.received_messages.first().content, '{"registrationId": 5678, "content": "test"}')
        self.assertEqual(self.user2.device.received_messages.first().senderRegistrationId, 1234)
        self.assertEqual(self.user2.device.received_messages.first().senderAddress, 'test1.1')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], 2)

    def test_receive_message(self):
        """Messages can be recieved"""
        response = self.client.get('/v1/1234/messages/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, list), True)
        self.assertEqual(response.data[0]['id'], 1)

    def test_delete_message(self):
        """Messages can be deleted"""
        response = self.client.delete('/v1/1234/messages/', [1], format='json')
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.device.received_messages.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, list), True)
        self.assertEqual(response.data[0], "message_deleted")

    def test_non_existant_recipient_message(self):
        """Messages with a non-existent recipient email are rejected"""
        response = self.client.post('/v1/1234/messages/', {
            "recipient": "testuser3@test.com",
            "message": '{"registrationId": 5678, "content": "test"}'
        }, format='json')
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.device.received_messages.count(), 1)
        self.assertEqual(self.user2.device.received_messages.count(), 0)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], "no_recipient")

    def test_incorrectly_formatted_email_message(self):
        """Messages with an incorrectly formatted recipient email are rejected"""
        response = self.client.post('/v1/1234/messages/', {
            "recipient": "test",
            "message": '{"registrationId": 5678, "content": "test"}'
        }, format='json')
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.device.received_messages.count(), 1)
        self.assertEqual(self.user2.device.received_messages.count(), 0)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['code'], "invalid_recipient_email")


    def test_no_json_message(self):
        """Messages which do not cotain a JSON string in the content are rejected"""
        response = self.client.post('/v1/1234/messages/', {
            "recipient": "testuser2@test.com",
            "message": 'notjson'
        }, format='json')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.device.received_messages.count(), 0)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], "incorrect_arguments")

    def test_changed_identity_send_message(self):
        """Messages sent from an altered identity are rejected"""
        response = self.client.post('/v1/1235/messages/', {
            "recipient": "testuser2@test.com",
            "message": '{"registrationId": 5678, "content": "test"}'
        }, format='json')
        self.user2.refresh_from_db()
        self.assertEqual(self.user2.device.received_messages.count(), 0)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], "device_changed")

    def test_changed_identity_receive_message(self):
        """Messages sent from an altered identity are rejected"""
        response = self.client.get('/v1/1235/messages/')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], "device_changed")

    def test_changed_identity_delete_message(self):
        """Messages sent from an altered identity are rejected"""
        response = self.client.delete('/v1/1235/messages/', [1], format='json')
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.device.received_messages.count(), 1)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['code'], "device_changed")

    def test_no_messages_available(self):
        """Getting messages when none are available returns an empty array"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/v1/5678/messages/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, list), True)
        self.assertEqual(len(response.data), 0)

    def test_delete_message_not_owner(self):
        """User cannot delete messages they do not own"""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete('/v1/5678/messages/', [1], format='json')
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.assertEqual(self.user1.device.received_messages.count(), 1)
        self.assertEqual(self.user2.device.received_messages.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(isinstance(response.data, list), True)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0], 'not_message_owner')

    def test_put_message(self):
        """The /messages PUT method should fail"""
        response = self.client.put('/v1/1234/messages/', [], format='json')
        self.assertEqual(response.status_code, 405)
