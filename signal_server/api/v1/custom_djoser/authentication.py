from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from nacl.exceptions import BadSignatureError
import nacl.signing
import base64, json
import datetime
import pytz
from urllib.parse import quote

class TokenAuthenticationWithSignature(TokenAuthentication):

    def authenticate(self, request):
        user_auth_tuple = super().authenticate(request)

        if user_auth_tuple is None:
            return
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
        signingKey = base64.b64decode(user.device.signingKey)
        verifyKey = nacl.signing.VerifyKey(signingKey)

        try:
            print("Verifying")
            verifyKey.verify(str.encode(signatureString), base64.b64decode(signature))
        except BadSignatureError:
            print("Verification error")
            return None
            
        print("Returning")
        return (user, token)