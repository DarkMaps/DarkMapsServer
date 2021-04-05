"""
Defines Django models
"""

from django.db import models
from django.conf import settings

class Device(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Identity key length is 44 text characters
    identity_key = models.CharField(max_length=44, blank=False)
    registration_id = models.PositiveIntegerField(blank=False)
    address = models.CharField(max_length=100, blank=False)
    class Meta:
        unique_together = ('user', 'address',)

class PreKey(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    key_id = models.PositiveIntegerField(blank=False)
    # Public key length is 44 text characters
    public_key = models.CharField(max_length=44, blank=False)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['device', 'key_id'], name='unique_key_id')
        ]


class SignedPreKey(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    key_id = models.PositiveIntegerField(blank=False)
    # Public key length is 44 text characters
    public_key = models.CharField(max_length=44, blank=False)
    # Signature length is 88 text characters
    signature = models.CharField(max_length=88, blank=False)

class Message(models.Model):
    recipient = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="received_messages")
    created = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=1000, blank=False)
    sender_registration_id = models.PositiveIntegerField(blank=False)
    sender_address = models.CharField(max_length=100, blank=False)
    class Meta:
        ordering = ('created',)
