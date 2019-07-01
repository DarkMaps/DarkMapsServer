from rest_framework import serializers
from signal_server.api.v1.models import Message, Device, PreKey, SignedPreKey
from django.core.exceptions import PermissionDenied, FieldError
from rest_framework.validators import UniqueValidator

class MessageSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    senderAddress = serializers.CharField(max_length=100, min_length=0)
    senderRegistrationId = serializers.IntegerField(min_value=0, max_value=999999)
    content = serializers.CharField(max_length=1000, min_length=0)
    recipientAddress = serializers.SerializerMethodField('get_recipient_address')
    def create(self, validated_data):
        recipientDevice = self.context['recipientDevice']
        return Message.objects.create(recipient=recipientDevice, **validated_data)
    def get_recipient_address(self, obj):
        return obj.recipient.address

class PreKeySerializer(serializers.Serializer):
    keyId = serializers.IntegerField(min_value=0, max_value= 999999)
    publicKey = serializers.CharField(max_length=44, min_length=44)
    def create(self, validated_data):
        user = self.context['user']
        registrationId = self.context['registrationId']
        deviceReference = Device.objects.filter(user=user, registrationId=registrationId).get()
        # Limit to max 100 prekeys
        if deviceReference.prekey_set.count() > 99:
            raise PermissionDenied()
        # Check an existing prekey does not have the same ID
        if not deviceReference.prekey_set.filter(keyId = validated_data['keyId']).count() == 0:
            raise FieldError()
        return PreKey.objects.create(device=deviceReference, **validated_data)

class SignedPreKeySerializer(serializers.Serializer):
    keyId = serializers.IntegerField(min_value=0, max_value=999999)
    publicKey = serializers.CharField(max_length=44, min_length=44)
    signature = serializers.CharField(max_length=88, min_length=88)
    def create(self, validated_data):
        user = self.context['user']
        registrationId = self.context['registrationId']
        deviceReference = Device.objects.filter(user=user, registrationId=registrationId).get()
        return SignedPreKey.objects.create(device=deviceReference, **validated_data)

class DeviceSerializer(serializers.Serializer):
    identityKey = serializers.CharField(max_length=44, min_length=44)
    address = serializers.CharField(max_length=100)
    registrationId = serializers.IntegerField(min_value=0, max_value=999999)
    signingKey = serializers.CharField(max_length=44, min_length=44)
    preKeys = PreKeySerializer(many=True)
    signedPreKey = SignedPreKeySerializer()
    signatureCount = serializers.IntegerField(min_value=0, max_value=99999999, required=False, default=0)
    def create(self, validated_data):
        user = self.context['user']
        # Limit to max 1 device for security reasons
        if hasattr(user, "device"):
            raise PermissionDenied()
        signedPreKey = validated_data.pop('signedPreKey')
        preKeys = validated_data.pop('preKeys')
        deviceReference = Device.objects.create(user=user, **validated_data)
        SignedPreKey.objects.create(device=deviceReference, **signedPreKey)
        for x in preKeys:
            PreKey.objects.create(device=deviceReference, **x)
        return deviceReference

    def update(self, instance, validated_data):
        instance.signatureCount = validated_data.get('signatureCount', instance.signatureCount)
        instance.save()
        return instance

class PreKeyBundleSerializer(serializers.Serializer):
    address = serializers.CharField(max_length=100, min_length=1)
    identityKey = serializers.CharField(max_length=33, min_length=33)
    registrationId = serializers.IntegerField(min_value=0, max_value=999999)
    preKey = PreKeySerializer(required=False)
    signedPreKey = SignedPreKeySerializer()

