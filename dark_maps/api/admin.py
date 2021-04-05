"""
Configures administration site
"""

from django.contrib import admin
from dark_maps.api.v1.models import Message, Device, PreKey, SignedPreKey

# Register your models here.
# class MessageAdmin(admin.ModelAdmin):
#     pass
admin.site.register(Message)

# class DeviceAdmin(admin.ModelAdmin):
#     pass
admin.site.register(Device)

# class PreKeyAdmin(admin.ModelAdmin):
#     pass
admin.site.register(PreKey)

# class SignedPreKeyAdmin(admin.ModelAdmin):
#     pass
admin.site.register(SignedPreKey)
