"""signal_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.conf.urls import url, include
from signal_server.api import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # API URLs
    url(r'^messages/(?P<requestedDeviceRegistrationID>[0-9]+)/$', views.MessageList.as_view()),
    url(r'^device/', views.DeviceView.as_view()),
    url(r'^prekeybundle/(?P<recipientEmail>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<ownDeviceRegistrationID>[0-9]+)/$', views.PreKeyBundleView.as_view()),
    url(r'^prekeys/(?P<requestedDeviceRegistrationID>[0-9]+)/$', views.UserPreKeys.as_view()),
    url(r'^signedprekey/(?P<requestedDeviceRegistrationID>[0-9]+)/$', views.UserSignedPreKeys.as_view()),

    # Auth URLs
    url(r'^auth/', include('trench.urls')), # Base endpoints
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('trench.urls.simplejwt')),
    url(r'^auth/password/reset/confirm(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view()),
    url(r'^auth/password/reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Admin URLs
    path('admin/', admin.site.urls),
]
