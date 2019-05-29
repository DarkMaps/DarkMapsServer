from django.conf.urls import url, include
from api import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # API URLs
    url(r'^messages/(?P<requestedDeviceRegistrationID>[0-9]+)/$', views.MessageList.as_view()),
    url(r'^device/', views.DeviceView.as_view()),
    url(r'^prekeybundle/(?P<recipientEmail>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<ownDeviceRegistrationID>[0-9]+)/$', views.PreKeyBundleView.as_view()),
    url(r'^prekeys/(?P<requestedDeviceRegistrationID>[0-9]+)/$', views.UserPreKeys.as_view()),
    url(r'^signedprekey/(?P<requestedDeviceRegistrationID>[0-9]+)/$', views.UserSignedPreKeys.as_view()),

    # Auth URLs
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.jwt')),
    url(r'^auth/password/reset/confirm(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view()),
    url(r'^auth/password/reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]