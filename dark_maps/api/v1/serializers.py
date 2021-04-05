"""
Defines Django serialisers
"""

from rest_framework import serializers
from dark_maps.api.v1.models import Message, Device, PreKey, SignedPreKey
from django.core.exceptions import PermissionDenied, FieldError

class MessageSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    sender_address = serializers.CharField(max_length=100, min_length=0)
    sender_registration_id = serializers.IntegerField(min_value=0, max_value=999999)
    content = serializers.CharField(max_length=1000, min_length=0)
    recipient_address = serializers.SerializerMethodField()
    def create(self, validated_data):
        recipient_device = self.context['recipient_device']
        return Message.objects.create(recipient=recipient_device, **validated_data)
    @classmethod
    def get_recipient_address(cls, obj):
        return obj.recipient.address

class PreKeySerializer(serializers.Serializer):
    key_id = serializers.IntegerField(min_value=0, max_value=999999)
    public_key = serializers.CharField(max_length=44, min_length=44)
    def create(self, validated_data):
        user = self.context['user']
        registration_id = self.context['registration_id']
        deviceReference = Device.objects.filter(user=user, registration_id=registration_id).get()
        # Limit to max 100 prekeys
        if deviceReference.prekey_set.count() > 99:
            raise PermissionDenied()
        # Check an existing prekey does not have the same ID
        if not deviceReference.prekey_set.filter(key_id=validated_data['key_id']).count() == 0:
            raise FieldError()
        return PreKey.objects.create(device=deviceReference, **validated_data)

class SignedPreKeySerializer(serializers.Serializer):
    key_id = serializers.IntegerField(min_value=0, max_value=999999)
    public_key = serializers.CharField(max_length=44, min_length=44)
    signature = serializers.CharField(max_length=88, min_length=88)
    def create(self, validated_data):
        user = self.context['user']
        registration_id = self.context['registration_id']
        deviceReference = Device.objects.filter(user=user, registration_id=registration_id).get()
        return SignedPreKey.objects.create(device=deviceReference, **validated_data)

class DeviceSerializer(serializers.Serializer):
    identity_key = serializers.CharField(max_length=44, min_length=44)
    address = serializers.CharField(max_length=100)
    registration_id = serializers.IntegerField(min_value=0, max_value=999999)
    pre_keys = PreKeySerializer(many=True)
    signed_pre_key = SignedPreKeySerializer()
    def create(self, validated_data):
        user = self.context['user']
        # Limit to max 1 device for security reasons
        if hasattr(user, "device"):
            raise PermissionDenied()
        signed_pre_key = validated_data.pop('signed_pre_key')
        pre_keys = validated_data.pop('pre_keys')
        deviceReference = Device.objects.create(user=user, **validated_data)
        SignedPreKey.objects.create(device=deviceReference, **signed_pre_key)
        for x in pre_keys:
            PreKey.objects.create(device=deviceReference, **x)
        return deviceReference

class PreKeyBundleSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=100, min_length=1)
    identity_key = serializers.CharField(max_length=33, min_length=33)
    registration_id = serializers.IntegerField(min_value=0, max_value=999999)
    pre_key = PreKeySerializer(required=False)
    signed_pre_key = SignedPreKeySerializer()
