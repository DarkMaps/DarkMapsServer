"""
Contains customised default serialisers
"""

from rest_framework import serializers

class CurrentPasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'invalid_password': 'Invalid password.',
    }

    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if is_password_valid:
            return value
        self.fail('invalid_password')
        return None

class UserDeleteSerializer(CurrentPasswordSerializer):
    pass
