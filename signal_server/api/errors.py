from rest_framework import status
from rest_framework.response import Response

no_user = Response({
    "code": "no_user",
    "message": "User does not exist"
}, status=status.HTTP_400_BAD_REQUEST)

no_recipient = Response({
    "code": "no_recipient",
    "message": "The recipient for your message does not exist"
}, status=status.HTTP_404_NOT_FOUND)

no_device = Response({
    "code": "no_device",
    "message": "User has not yet registered a device"
}, status=status.HTTP_404_NOT_FOUND)

no_recipient_device = Response({
    "code": "no_recipient_device",
    "message": "Recipient has not yet registered a device"
}, status=status.HTTP_404_NOT_FOUND)

device_exists = Response({
    "code": "device_exists",
    "message": "A device has already been created for this user"
}, status=status.HTTP_403_FORBIDDEN)

device_changed = Response({
    "code": "device_changed",
    "message": "Own device has changed"
}, status=status.HTTP_403_FORBIDDEN)

recipient_identity_changed = Response({
    "code": "recipient_identity_changed",
    "message": "Recipients device has changed"
}, status=status.HTTP_403_FORBIDDEN)

invalid_recipient_address = Response({
    "code": "invalid_recipient_address",
    "message": "Recipients address was invalid"
}, status=status.HTTP_400_BAD_REQUEST)

reached_max_prekeys = Response({
    "code": "reached_max_prekeys",
    "message": "User has reached the maximum number of prekeys allowed"
}, status=status.HTTP_400_BAD_REQUEST)

prekey_id_exists = Response({
    "code": "prekey_id_exists",
    "message": "A prekey with that keyId already exists"
}, status=status.HTTP_400_BAD_REQUEST)

invalid_recipient_email = Response({
    "code": "invalid_recipient_email",
    "message": "The email provided for the recipient is incorrectly formatted"
}, status=status.HTTP_400_BAD_REQUEST)

error_incrementing = Response({
    "code": "error_incrementing",
    "message": "There was an error incrementing the signing counter"
}, status=status.HTTP_400_BAD_REQUEST)


# This error is appended to a list of responses when trying to process 
# multiple messages, so should NOT be in the Response() format
not_message_owner = {
    "code": "not_message_owner",
    "message": "You do not own one of the messages you are trying to delete"
}

# This error is appended to a list of responses when trying to process 
# multiple messages, so should NOT be in the Response() format
non_existant_message = {
    "code": "non-existant_message",
    "message": "One of the messages you are trying to delete does not exist"
}

def incorrectArguments(explanation):
    data = {
        "code": "incorrect_arguments",
        "message": "Incorrect arguments were provided in the request"
    }
    if explanation:
        data['explanation'] = explanation
    return Response(data, status=status.HTTP_403_FORBIDDEN)

def invalidSerializerData(errors):
    return Response({
        "code": "invalid_data",
        "message": "Invalid data provided was provided in the request",
        "errors": errors
    }, status=status.HTTP_400_BAD_REQUEST)