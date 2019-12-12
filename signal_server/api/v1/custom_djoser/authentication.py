"""
Enforces request signing as appropriate
"""
import base64
import json
import datetime

from urllib.parse import quote

from jose import jws

from rest_framework.authentication import TokenAuthentication

from django.core.exceptions import ObjectDoesNotExist

class TokenAuthenticationWithSignature(TokenAuthentication):

    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)

        if user_auth_tuple is None:
            return None
        (user, token) = user_auth_tuple

        # Check logged in
        if (not 'Authorization' in request.headers):
            return None

        # Check signature exists
        if (not 'Signature' in request.headers):
            return None

        # Check user has a device
        try:
            user.device
        except ObjectDoesNotExist:
            return None

        print("Splitting signature")
        # Split signature into time and signature
        signature = request.headers['Signature'].split(":", 1)
        if len(signature) != 2:
            return None
        signatureTime = signature[0]
        signature = signature[1]

        # Check signature hasn't expired
        print("Checking expiry")
        expiryTime = datetime.datetime.now() + datetime.timedelta(minutes=5)
        expiryTime = expiryTime.timestamp() * 1000
        if (float(signatureTime) > expiryTime):
            print("Expiry error")
            return None

        # Create signature string to check
        print("Creating string")
        signatureString = signatureTime + request.method + quote(request.path.encode("utf-8"), safe='')
        if (request.method == "POST" or request.method == "DELETE"):
            bodyString = json.dumps(json.loads(request.body), ensure_ascii=False, indent=None, separators=(',', ':'))
            bodyString = quote(bodyString.encode("utf-8"), safe='()!*\'')
            signatureString = signatureString + bodyString

        # Get signingKey
        print("Creating key")
        signingKey = json.loads(user.device.signingKey)

        try:
            print("Verifying")
            verificationSignatureString = jws.verify(signature, signingKey, 'ES512').decode("utf-8")
            if (verificationSignatureString != signatureString):
                raise Exception("verification error")
        except Exception as e:
            print(e)
            print("Verification error")
            return None

        print("Returning")
        return (user, token)
