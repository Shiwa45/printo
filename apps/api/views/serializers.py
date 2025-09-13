# apps/api/views/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password_confirm', 'phone', 'company_name']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'company_name', 'gst_number', 'is_verified', 'date_joined']
        read_only_fields = ['id', 'email', 'is_verified', 'date_joined']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file uploads"""
    file = serializers.FileField()
    type = serializers.ChoiceField(choices=['asset', 'template', 'export'], default='asset')
    
    def validate_file(self, value):
        # Check file size (10MB limit)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Check file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'svg', 'pdf', 'json']
        file_extension = value.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            raise serializers.ValidationError(f"File type '{file_extension}' is not allowed")
        
        return value


class PricingCalculationSerializer(serializers.Serializer):
    """Serializer for pricing calculations"""
    product_slug = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)
    specifications = serializers.JSONField(required=False, default=dict)
    
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        if value > 10000:
            raise serializers.ValidationError("Quantity cannot exceed 10,000")
        return value