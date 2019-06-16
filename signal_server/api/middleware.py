from signal_server.api.serializers import DeviceSerializer
from rest_framework.response import Response
from rest_framework import status

class SignatureCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        print(response.status_code)

        # If user tried to authorise
        if ('Authorization' in request.headers and 'Signature' in request.headers):
            # And if user not unauthorised
            if (not response.status_code == 401):
                print("Increment Here")
                print(request.user)
                print(request.user.device.signatureCount)
                currentDevice = request.user.device
                serializer = DeviceSerializer(currentDevice, data={'signatureCount': currentDevice.signatureCount + 1}, partial=True)
                if not serializer.is_valid():
                    print(serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR).render()
                else: 
                    serializer.save()


        # Code to be executed for each request/response after
        # the view is called.

        return response