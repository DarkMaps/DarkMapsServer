from django.contrib import admin
from signal_server.api.models import Message, Device, PreKey, SignedPreKey

# Register your models here.
class MessageAdmin(admin.ModelAdmin):
    pass
admin.site.register(Message, MessageAdmin)

class DeviceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Device, DeviceAdmin)

class PreKeyAdmin(admin.ModelAdmin):
    pass
admin.site.register(PreKey, PreKeyAdmin)

class SignedPreKeyAdmin(admin.ModelAdmin):
    pass
admin.site.register(SignedPreKey, SignedPreKeyAdmin)