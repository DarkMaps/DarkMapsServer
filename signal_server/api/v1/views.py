"""
Defines Django views
"""
import json
import re
import logging
import time

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, FieldError
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver

from signal_server.api.v1.models import Message, Device
from signal_server.api.v1.serializers import MessageSerializer, DeviceSerializer, PreKeyBundleSerializer, PreKeySerializer, SignedPreKeySerializer
from signal_server.api.v1 import errors

from djoser.signals import user_registered

from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class MessageList(APIView):

    authentication_classes = (TokenAuthentication, )

    # User can get a list of messages for their device
    def get(self, request, **kwargs):
        user = self.request.user
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Get Messages] [Started]")

        # Check correct arguments provided
        if 'requestedDeviceregistration_id' not in kwargs:
            logger.error(f"[Get Messages] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")

        # Check device exists and owned by user
        if not hasattr(user, "device"):
            logger.error(f"[Get Messages] [Error - User has no device]")
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['requestedDeviceregistration_id']) != user.device.registration_id:
            logger.error(f"[Get Messages] [Error - Device changed]")
            return errors.device_changed

        messages = user.device.received_messages.all()
        serializer = MessageSerializer(messages, many=True)
        toc = time.perf_counter()
        logger.info(f"[Get messages] [Complete] [{toc - tic:0.4f}]")
        return Response(serializer.data, status=status.HTTP_200_OK)

    # User can post messages.
    def post(self, request, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Post Messages] [Started]")

        # Check correct arguments provided
        if 'requestedDeviceregistration_id' not in kwargs:
            logger.error(f"[Post Messages] [Error - Incorrect Arguments]")
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")
        if not (hasattr(request, "data") & isinstance(request.data, object) & (not isinstance(request.data, list))):
            logger.error(f"[Post Messages] [Error - Incorrect Arguments]")
            return errors.incorrectArguments("The request body must include the message in JSON object format.")
        if not (("recipient" in request.data) & isinstance(request.data["recipient"], str)):
            logger.error(f"[Post Messages] [Error - Incorrect Arguments]")
            return errors.incorrectArguments("The request body must include the recipient's email address in the 'recipient' field.")
        if not (("message" in request.data) & isinstance(request.data["message"], str)):
            logger.error(f"[Post Messages] [Error - Incorrect Arguments]")
            return errors.incorrectArguments("The request body must include the message content in the 'message' field.")

        ownUser = self.request.user
        recipientEmail = request.data["recipient"]
        emailPattern = re.compile(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])')
        if not (emailPattern.match(recipientEmail.lower())):
            logger.error(f"[Post Messages] [Error - Invalid Email]")
            return errors.invalid_recipient_email

        try:
            messageDataParsed = json.loads(request.data['message'])
        except Exception:
            logger.error(f"[Post Messages] [Error - Incorrect Arguments]")
            return errors.incorrectArguments("The request body must include the message content in JSON string format in the 'message' field.")

        # Check device exists and owned by user
        if not hasattr(ownUser, "device"):
            logger.error(f"[Post Messages] [Error - User has no device]")
            return errors.no_device

        # Check own device ID has not changed
        if int(kwargs['requestedDeviceregistration_id']) != ownUser.device.registration_id:
            logger.error(f"[Post Messages] [Error - Device changed]")
            return errors.device_changed

        # Check repient user exists
        recipientUser = {}
        userModel = get_user_model()
        try:
            recipientUser = userModel.objects.get(email=recipientEmail)
        except Exception:
            logger.error(f"[Post Messages] [Error - Recipient doesn't exist]")
            return errors.no_recipient_user

        # Check recipient device exists
        if not hasattr(recipientUser, "device"):
            logger.error(f"[Post Messages] [Error - Recipient has no device]")
            return errors.no_recipient_device
        recipient_device = recipientUser.device

        # Check recipient device registration_id matches that sent in message
        if not (recipientUser.device.registration_id == int(messageDataParsed['registration_id'])):
            logger.error(f"[Post Messages] [Error - Recipient identity changed]")
            return errors.recipient_identity_changed

        serializer = MessageSerializer(data={'content': request.data['message'], 'sender_address':ownUser.device.address, 'sender_registration_id':ownUser.device.registration_id}, context={'recipient_device': recipient_device})
        if not serializer.is_valid():
            logger.error("[Post Messages] [Error - MessageSerialiser returned invalid response]")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        toc = time.perf_counter()
        logger.info(f"[Post Messages] [Complete] [{toc - tic:0.4f}]")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # User can delete any message for which they are the recipient
    def delete(self, request, **kwargs):

        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Delete Message] [Started]")

        # Check correct arguments provided
        if 'requestedDeviceregistration_id' not in kwargs:
            logger.error(f"[Delete Message] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")
        if not (hasattr(request, "data") and isinstance(request.data, list) and len(request.data) > 0):
            logger.error(f"[Delete Message] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request body must include the message IDs to be deleted in list format.")

        user = self.request.user
        messageList = request.data
        response = []

        # Check device exists and owned by user
        if not hasattr(user, "device"):
            logger.error(f"[Delete Message] [Error - User has no device]")
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['requestedDeviceregistration_id']) != user.device.registration_id:
            logger.error(f"[Delete Message] [Error - Device changed]")
            return errors.device_changed

        for message_id in messageList:
            try:
                message = Message.objects.get(id=message_id)
                # Check user owns message
                if not message.recipient.user == user:
                    logger.error(f"[Delete Message] [Error - Message not owned by user]")
                    response.append(errors.not_message_owner)
                else:
                    message.delete()
                    response.append('message_deleted')
            except Exception:
                logger.error(f"[Delete Message] [Error - Tried to delete non-existant message]")
                response.append(errors.non_existant_message)

        toc = time.perf_counter()
        logger.info(f"[Delete Message] [Complete] [{toc - tic:0.4f}]")
        return Response(response, status=status.HTTP_200_OK)

class DeviceView(APIView):

    authentication_classes = (TokenAuthentication, )

    def get(self, request, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Get Device] [Started]")
        user = self.request.user
        # Check device exists and owned by user
        if not hasattr(user, "device"):
            logger.error(f"[Get Device] [Error - Tried to get non-existant device]")
            return errors.no_device
        device = model_to_dict(user.device)
        toc = time.perf_counter()
        logger.info(f"[Delete Message] [Complete] [{toc - tic:0.4f}]")
        return Response(device, status=status.HTTP_200_OK)

    # User can register details of a new device
    def post(self, request, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Post Device] [Started]")

        # Check correct arguments provided
        # Note - do not verify registration_id here as device should not exist
        if not (hasattr(request, "data") & isinstance(request.data, object)):
            logger.error(f"[Post Device] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request body must include the device details in JSON object format.")

        user = self.request.user

        # Check device does not already exist
        if hasattr(user, "device"):
            logger.error(f"[Post Device] [Error - Device already exists]")
            return errors.device_exists

        deviceData = request.data
        serializer = DeviceSerializer(data=deviceData, context={'user': user})

        if not serializer.is_valid():
            logger.error(f"[Post Device] [Error - DeviceSerializer returned invalid]")
            return errors.invalidSerializerData(serializer.errors)

        serializer.save()
        toc = time.perf_counter()
        logger.info(f"[Post Device] [Complete] [{toc - tic:0.4f}]")
        return Response({"code": "device_created", "message": "Device successfully created"}, status=status.HTTP_201_CREATED)

    # User can delete a device they own
    def delete(self, requested, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Delete Device] [Started]")

        user = self.request.user
        # Check device exists and owned by user
        if not hasattr(user, "device"):
            logger.error(f"[Delete Device] [Error - Tried to delete non-existant device]")
            return errors.no_device
        device = user.device
        device.delete()
        toc = time.perf_counter()
        logger.info(f"[Delete Device] [Complete] [{toc - tic:0.4f}]")
        return Response({"code": "device_deleted", "message": "Device successfully deleted"}, status=status.HTTP_204_NO_CONTENT)


class PreKeyBundleView(APIView):
    throttle_scope = 'pre_keyBundle'
    authentication_classes = (TokenAuthentication, )

    # User can optain a pre_keyBundle from another user
    def get(self, request, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Get Prekey Bundle] [Started]")

        ownUser = self.request.user

        # Check correct arguments provided
        if not (('recipient_address' in kwargs) & ('ownDeviceregistration_id' in kwargs)):
            logger.error(f"[Get Prekey Bundle] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request URL must include the recipient's address and the sender's registration ID")

        if not (isinstance(kwargs['recipient_address'], str)):
            logger.error(f"[Get Prekey Bundle] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The recipient's address must be provided as a string")

        # Check device exists and owned by user
        if not hasattr(ownUser, "device"):
            logger.error(f"[Get Prekey Bundle] [Error - User has no device]")
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['ownDeviceregistration_id']) != ownUser.device.registration_id:
            logger.error(f"[Get Prekey Bundle] [Error - Device changed]")
            return errors.device_changed

        # Decode hex
        try:
            recipient_address = bytearray.fromhex(kwargs['recipient_address']).decode()
        except Exception:
            logger.error(f"[Get Prekey Bundle] [Error - Unable to decode hex]")
            return errors.incorrectArguments("The recipient's address must be encoded in HEX format")
        try:
            email = recipient_address.rpartition('.')[0]
            User = get_user_model()
            user = User.objects.get(email=email)
        except Exception as e:
            logger.error(f"[Get Prekey Bundle] [Error - Tried to get prekey bundle for non-existant user]")
            return errors.no_recipient_user
        try:
            device = Device.objects.get(address=recipient_address)
        except Exception:
            logger.error(f"[Get Prekey Bundle] [Error - Tried to get prekey bundle for non-existant device]")
            return errors.no_recipient_device

        pre_keyBundle = device.__dict__
        pre_keyBundle['signed_pre_key'] = device.signedprekey

        # Build pre key bundle, removing a pre_key from the requested user's list
        if (device.prekey_set.count() > 0):
            pre_keyToReturn = device.prekey_set.all()[:1].get()
            pre_keyBundle['pre_key'] = pre_keyToReturn
            # Update stored pre key
            pre_keyToReturn.delete()

        serializer = PreKeyBundleSerializer(pre_keyBundle)

        toc = time.perf_counter()
        logger.info(f"[Get Prekey Bundle] [Complete] [{toc - tic:0.4f}]")
        # Return bundle
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserPreKeys(APIView):

    authentication_classes = (TokenAuthentication, )

    # User can post a new set of pre_keys
    def post(self, request, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Post Pre-Keys] [Started]")

        try:

            user = self.request.user

            # Check correct arguments provided
            if 'requestedDeviceregistration_id' not in kwargs:
                logger.error(f"[Post Pre-Keys] [Error - Incorrect Arguments]")
                return errors.incorrectArguments("The request URL must include the user's own registration ID")
            if not ((hasattr(request, "data")) & (isinstance(request.data, list)) & (len(request.data) > 0)):
                logger.error(f"[Post Pre-Keys] [Error - Incorrect Arguments]")
                return errors.incorrectArguments("The request body must be in list format and have a length of at least one.")

             # Check device exists and owned by user
            if not hasattr(user, "device"):
                logger.error(f"[Post Pre-Keys] [Error - User has no device]")
                return errors.no_device

            # Check device ID has not changed
            if int(kwargs['requestedDeviceregistration_id']) != user.device.registration_id:
                logger.error(f"[Post Pre-Keys] [Error - Device changed]")
                return errors.device_changed

            newPreKeys = request.data

            for x in newPreKeys:
                serializer = PreKeySerializer(data=x, context={'user': user, 'registration_id': user.device.registration_id})

                if not serializer.is_valid():
                    logger.error(f"[Post Pre-Keys] [Error - PreKeySerializer returned invalid]")
                    return errors.invalidSerializerData(serializer.errors)

                serializer.save()

            toc = time.perf_counter()
            logger.info(f"[Post Pre-Keys] [Complete] [{toc - tic:0.4f}]")
            return Response({"code": "prekeys_stored", "message": "Prekeys successfully stored"}, status=status.HTTP_200_OK)

        except PermissionDenied:
            logger.error(f"[Post Pre-Keys] [Error - Reached Max PreKeys]")
            return errors.reached_max_prekeys
        except FieldError:
            logger.error(f"[Post Pre-Keys] [Error - Prekey ID Exists]")
            return errors.prekey_id_exists
        except:
            logger.critical(f"[Post Pre-Keys] [Error - Unexpected Error: {sys.exc_info()[0]}]")


class UserSignedPreKeys(APIView):

    authentication_classes = (TokenAuthentication, )

    # User can post a new signed_pre_key
    def post(self, request, **kwargs):
        logger = logging.getLogger("watchtower")
        tic = time.perf_counter()
        logger.info(f"[Post Signed Pre-Key] [Started]")

        user = self.request.user

        # Check correct arguments provided
        if 'requestedDeviceregistration_id' not in kwargs:
            logger.error(f"[Post Signed Pre-Key] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")
        if not (hasattr(request, "data") & isinstance(request.data, object) & (not isinstance(request.data, list))):
            logger.error(f"[Post Signed Pre-Key] [Error - Incorrect arguments]")
            return errors.incorrectArguments("The request body must include the signed prekey in JSON object format.")

        # Check device exists and owned by user
        if not hasattr(user, "device"):
            logger.error(f"[Post Signed Pre-Key] [Error - User has no device]")
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['requestedDeviceregistration_id']) != user.device.registration_id:
            logger.error(f"[Post Signed Pre-Key] [Error - Device changed]")
            return errors.device_changed

        serializer = SignedPreKeySerializer(data=request.data, context={'user': user, 'registration_id': user.device.registration_id})

        if not serializer.is_valid():
            logger.error(f"[Post Signed Pre-Key] [Error - SignedPreKeySerializer returned invalid]")
            return errors.invalidSerializerData(serializer.errors)

        user.device.signedprekey.delete()
        serializer.save()
        toc = time.perf_counter()
        logger.info(f"[Post Signed Pre-Key] [Complete] [{toc - tic:0.4f}]")
        return Response({"code": "signed_prekey_stored", "message": "Signed prekey successfully stored"}, status=status.HTTP_200_OK)

@receiver(post_delete, sender=User)
def user_delete_callback(sender, **kwargs):
    userModel = get_user_model()
    userCount = userModel.objects.count()
    logger = logging.getLogger("watchtower")
    logger.info(f"[User Deleted] [{userCount}]")

@receiver(user_registered)
def user_registered_callback(sender, **kwargs):
    userModel = get_user_model()
    userCount = userModel.objects.count()
    logger = logging.getLogger("watchtower")
    logger.info(f"[User Registered] [{userCount}]")
