"""
Defines Django URLs
"""

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from signal_server.api.v1 import views as v1_views

v1_urlpatterns = [
    # API URLs
    url(r'^devices/', v1_views.DeviceView.as_view()),
    url(r'^(?P<requestedDeviceRegistrationID>[0-9]+)/prekeys/$', v1_views.UserPreKeys.as_view()),
    url(r'^(?P<requestedDeviceRegistrationID>[0-9]+)/signedprekeys/$', v1_views.UserSignedPreKeys.as_view()),
    url(r'^(?P<requestedDeviceRegistrationID>[0-9]+)/messages/$', v1_views.MessageList.as_view()),
    url(r'^prekeybundles/(?P<recipientAddress>[0-9A-Za-z./=+]+)/(?P<ownDeviceRegistrationID>[0-9]+)/$', v1_views.PreKeyBundleView.as_view()),

    # Auth URLs
    url(r'^auth/', include('trench.urls')), # Base endpoints
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('trench.urls.djoser')),  # for Token Based Authorization
    url(r'^auth/password/reset/confirm(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view()),
    url(r'^auth/password/reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Admin URLs
    path('admin/', admin.site.urls),
]
