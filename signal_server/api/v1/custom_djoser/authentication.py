"""
Enforces request signing as appropriate
"""

import json
import datetime
import base64
import binascii
import hashlib

from urllib.parse import quote

from ecdsa import VerifyingKey, NIST521p

# from cryptography.hazmat.primitives.asymmetric.ec import ECDSA, EllipticCurvePublicNumbers, SECP521R1
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.backends import default_backend


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

        # Split signature into time and signature
        signature = request.headers['Signature'].split(":", 1)
        if len(signature) != 2:
            return None
        signatureTime = signature[0]
        signature = signature[1]

        # Check signature hasn't expired
        expiryTime = datetime.datetime.now() + datetime.timedelta(minutes=5)
        expiryTime = expiryTime.timestamp() * 1000
        if (float(signatureTime) > expiryTime):
            print("Expiry error")
            return None

        # Create signature string to check
        signatureString = signatureTime + request.method + quote(request.path.encode("utf-8"), safe='')
        if (request.method == "POST" or request.method == "DELETE"):
            bodyString = json.dumps(json.loads(request.body), ensure_ascii=False, indent=None, separators=(',', ':'))
            bodyString = quote(bodyString.encode("utf-8"), safe='()!*\'')
            signatureString = signatureString + bodyString

        # Get signingKey
        signingKey = user.device.signingKey
        # signingKey = json.loads(user.device.signingKey)

        try:
            verifyingKey = VerifyingKey.from_string(binascii.unhexlify(signingKey), curve=NIST521p)
            digest = hashlib.sha256(signatureString.encode('utf-8')).digest()
            verifyingKey.verify_digest(base64.b64decode(signature), digest)
        except Exception as e:
            print(e)
            print("Verification error")
            return None

        return (user, token)
