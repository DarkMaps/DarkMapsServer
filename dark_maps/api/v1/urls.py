"""
Defines Django URLs
"""

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy, path
from django.views.decorators.csrf import csrf_exempt

from dark_maps.api.v1 import views as v1_views

v1_urlpatterns = [
    # API URLs
    url(r'^devices/', v1_views.DeviceView.as_view()),
    url(r'^(?P<requestedDeviceregistration_id>[0-9]+)/prekeys/$', v1_views.UserPreKeys.as_view()),
    url(r'^(?P<requestedDeviceregistration_id>[0-9]+)/signedprekeys/$', v1_views.UserSignedPreKeys.as_view()),
    url(r'^(?P<requestedDeviceregistration_id>[0-9]+)/messages/$', v1_views.MessageList.as_view()),
    url(r'^prekeybundles/(?P<recipient_address>[0-9A-Za-z./=+]+)/(?P<ownDeviceregistration_id>[0-9]+)/$', v1_views.PreKeyBundleView.as_view()),

    # Auth URLs
    url(r'^auth/', include('trench.urls')), # Base endpoints
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('trench.urls.djoser')),  # for Token Based Authorization
    # Note reuest password reset API endpoint:
    # POST /v1/auth/users/reset_password/ with {"email": "requested email body"}
    url(r'auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,35})/$', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html',success_url='/v1/auth/password/reset/complete/')),
    url(r'auth/password/reset/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html')),

]
