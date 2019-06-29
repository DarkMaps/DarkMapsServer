from rest_framework.authentication import TokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from nacl.exceptions import BadSignatureError
import nacl.signing
import base64, json
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
            
        # Create signature string to check
        signatureString = str(user.device.signatureCount) + quote(request.path.encode("utf-8"), safe='')
        if (request.method == "POST"):
            bodyString = json.dumps(json.loads(request.body), ensure_ascii=False, indent=None, separators=(',', ':'))
            bodyString = quote(bodyString.encode("utf-8"), safe='()!*\'')
            signatureString = signatureString + bodyString

        # Get signingKey
        signingKey = base64.b64decode(user.device.signingKey)
        verifyKey = nacl.signing.VerifyKey(signingKey)

        try:
            verifyKey.verify(str.encode(signatureString), base64.b64decode(request.headers['Signature']))
        except BadSignatureError:
            return None
            
        return (user, token)