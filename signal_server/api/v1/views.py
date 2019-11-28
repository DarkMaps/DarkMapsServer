"""
Defines Django views
"""
import json
import re

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, FieldError

from signal_server.api.v1.models import Message, Device, PreKey, SignedPreKey
from signal_server.api.v1.serializers import MessageSerializer, DeviceSerializer, PreKeyBundleSerializer, PreKeySerializer, SignedPreKeySerializer
from signal_server.api.v1 import errors
from signal_server.api.v1.custom_djoser.authentication import TokenAuthenticationWithSignature

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class MessageList(APIView):

    authentication_classes = (TokenAuthenticationWithSignature, )

    # User can get a list of messages for their device
    def get(self, request, **kwargs):
        user = self.request.user

        # Check correct arguments provided
        if 'requestedDeviceRegistrationID' not in kwargs:
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")

        # Check device exists and owned by user
        if not hasattr(user, "device"):
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['requestedDeviceRegistrationID']) != user.device.registrationId:
            return errors.device_changed

        messages = user.device.received_messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # User can post messages.
    def post(self, request, **kwargs):

        # Check correct arguments provided
        if 'requestedDeviceRegistrationID' not in kwargs:
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")
        if not (hasattr(request, "data") & isinstance(request.data, object) & (not isinstance(request.data, list))):
            return errors.incorrectArguments("The request body must include the message in JSON object format.")
        if not (("recipient" in request.data) & isinstance(request.data["recipient"], str)):
            return errors.incorrectArguments("The request body must include the recipient's email address in the 'recipient' field.")
        if not (("message" in request.data) & isinstance(request.data["message"], str)):
            return errors.incorrectArguments("The request body must include the message content in the 'message' field.")

        ownUser = self.request.user
        recipientEmail = request.data["recipient"]
        emailPattern = re.compile(r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])')
        if not (emailPattern.match(recipientEmail)):
            return errors.invalid_recipient_email

        try:
            messageDataParsed = json.loads(request.data['message'])
        except Exception:
            return errors.incorrectArguments("The request body must include the message content in JSON string format in the 'message' field.")

        # Check device exists and owned by user
        if not hasattr(ownUser, "device"):
            return errors.no_device

        # Check own device ID has not changed
        if int(kwargs['requestedDeviceRegistrationID']) != ownUser.device.registrationId:
            return errors.device_changed

        # Check repiient user exists
        recipientUser = {}
        userModel = get_user_model()
        try:
            recipientUser = userModel.objects.get(email=recipientEmail)
        except Exception:
            return errors.no_recipient

        # Check recipient device exists
        if not hasattr(recipientUser, "device"):
            return errors.no_recipient_device
        recipientDevice = recipientUser.device

        # Check recipient device registrationId matches that sent in message
        if not (recipientUser.device.registrationId == int(messageDataParsed['registrationId'])):
            return errors.recipient_identity_changed

        serializer = MessageSerializer(data={'content': request.data['message'], 'senderAddress':ownUser.device.address, 'senderRegistrationId':ownUser.device.registrationId}, context={'recipientDevice': recipientDevice})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # User can delete any message for which they are the recipient
    def delete(self, request, **kwargs):

        # Check correct arguments provided
        if 'requestedDeviceRegistrationID' not in kwargs:
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")
        if not (hasattr(request, "data") & isinstance(request.data, list) & len(request.data) > 0):
            return errors.incorrectArguments("The request body must include the message IDs to be deleted in list format.")

        user = self.request.user
        messageList = request.data
        response = []

        # Check device exists and owned by user
        if not hasattr(user, "device"):
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['requestedDeviceRegistrationID']) != user.device.registrationId:
            return errors.device_changed

        for messageId in messageList:
            try:
                message = Message.objects.get(id=messageId)
                # Check user owns message
                if not message.recipient.user == user:
                    response.append(errors.not_message_owner)
                else:
                    message.delete()
                    response.append('message_deleted')
            except Exception:
                response.append(errors.non_existant_message)

        return Response(response, status=status.HTTP_200_OK)

class DeviceView(APIView):

    # User can register details of a new device
    def post(self, request, **kwargs):

        # Check correct arguments provided
        # Note - do not verify registrationID here as device should not exist
        if not (hasattr(request, "data") & isinstance(request.data, object)):
            return errors.incorrectArguments("The request body must include the device details in JSON object format.")

        user = self.request.user

        # Check device does not already exist
        if hasattr(user, "device"):
            return errors.device_exists

        deviceData = request.data
        serializer = DeviceSerializer(data=deviceData, context={'user': user})

        if not serializer.is_valid():
            return errors.invalidSerializerData(serializer.errors)

        serializer.save()
        return Response({"code": "device_created", "message": "Device successfully created"}, status=status.HTTP_201_CREATED)

    # User can delete a device they own
    def delete(self, requested, **kwargs):

        user = self.request.user
        # Check device exists and owned by user
        if not hasattr(user, "device"):
            return errors.no_device
        device = user.device
        device.delete()
        return Response({"code": "device_deleted", "message": "Device successfully deleted"}, status=status.HTTP_204_NO_CONTENT)


class PreKeyBundleView(APIView):
    throttle_scope = 'preKeyBundle'
    authentication_classes = (TokenAuthenticationWithSignature, )
    # User can optain a preKeyBundle from another user
    def get(self, request, **kwargs):

        ownUser = self.request.user

        # Check correct arguments provided
        if not (('recipientAddress' in kwargs) & ('ownDeviceRegistrationID' in kwargs)):
            return errors.incorrectArguments("The request URL must include the recipient's address and the sender's registration ID")

        if not (isinstance(kwargs['recipientAddress'], str)):
            return errors.incorrectArguments("The recipient's address must be provided as a string")

        # Check device exists and owned by user
        if not hasattr(ownUser, "device"):
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['ownDeviceRegistrationID']) != ownUser.device.registrationId:
            return errors.device_changed


        # Decode hex
        try:
            recipientAddress = bytearray.fromhex(kwargs['recipientAddress']).decode()
        except Exception:
            return errors.incorrectArguments("The recipient's address must be encoded in HEX format")
        try:
            device = Device.objects.get(address=recipientAddress)
        except Exception:
            return errors.no_recipient_device

        preKeyBundle = device.__dict__
        preKeyBundle['signedPreKey'] = device.signedprekey

        # Build pre key bundle, removing a preKey from the requested user's list
        if (device.prekey_set.count() > 0):
            preKeyToReturn = device.prekey_set.all()[:1].get()
            preKeyBundle['preKey'] = preKeyToReturn
            # Update stored pre key
            preKeyToReturn.delete()

        serializer = PreKeyBundleSerializer(preKeyBundle)

        # Return bundle
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserPreKeys(APIView):

    authentication_classes = (TokenAuthenticationWithSignature, )

    # User can post a new set of preKeys
    def post(self, request, **kwargs):

        try:

            user = self.request.user

            # Check correct arguments provided
            if 'requestedDeviceRegistrationID' not in kwargs:
                return errors.incorrectArguments("The request URL must include the user's own registration ID")
            if not (hasattr(request, "data") & isinstance(request.data, list) & len(request.data) > 0):
                return errors.incorrectArguments("The request body must be in list format and have a length of at least one.")

             # Check device exists and owned by user
            if not hasattr(user, "device"):
                return errors.no_device

            # Check device ID has not changed
            if int(kwargs['requestedDeviceRegistrationID']) != user.device.registrationId:
                return errors.device_changed

            newPreKeys = request.data

            for x in newPreKeys:
                serializer = PreKeySerializer(data=x, context={'user': user, 'registrationId': user.device.registrationId})

                if not serializer.is_valid():
                    return errors.invalidSerializerData(serializer.errors)

                serializer.save()

            return Response({"code": "prekeys_stored", "message": "Prekeys successfully stored"}, status=status.HTTP_200_OK)

        except PermissionDenied:
            return errors.reached_max_prekeys
        except FieldError:
            return errors.prekey_id_exists


class UserSignedPreKeys(APIView):

    authentication_classes = (TokenAuthenticationWithSignature, )

    # User can post a new signedPreKey
    def post(self, request, **kwargs):

        user = self.request.user

        # Check correct arguments provided
        if 'requestedDeviceRegistrationID' not in kwargs:
            return errors.incorrectArguments("The request URL must include the user's own registration ID.")
        if not (hasattr(request, "data") & isinstance(request.data, object) & (not isinstance(request.data, list))):
            return errors.incorrectArguments("The request body must include the signed prekey in JSON object format.")

        # Check device exists and owned by user
        if not hasattr(user, "device"):
            return errors.no_device

        # Check device ID has not changed
        if int(kwargs['requestedDeviceRegistrationID']) != user.device.registrationId:
            return errors.device_changed

        serializer = SignedPreKeySerializer(data=request.data, context={'user': user, 'registrationId': user.device.registrationId})

        if not serializer.is_valid():
            return errors.invalidSerializerData(serializer.errors)

        user.device.signedprekey.delete()
        serializer.save()
        return Response({"code": "signed_prekey_stored", "message": "Signed prekey successfully stored"}, status=status.HTTP_200_OK)
