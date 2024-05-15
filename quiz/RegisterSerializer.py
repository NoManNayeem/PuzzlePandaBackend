from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile  # Ensure you import Profile correctly based on your project structure
from django.db import IntegrityError









from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    primary_phone = serializers.CharField(source='profile.primary_phone')
    operator = serializers.ChoiceField(choices=Profile.OPERATOR_CHOICES, source='profile.operator')
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('primary_phone', 'password', 'operator')

    def validate_primary_phone(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with that phone number already exists.")
        return value

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        username = profile_data['primary_phone']

        user = User.objects.create_user(
            username=username,
            password=validated_data['password']
        )
        profile, created = Profile.objects.get_or_create(user=user, defaults=profile_data)
        if not created:
            # Update existing profile if it was automatically created by the signal
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return user
