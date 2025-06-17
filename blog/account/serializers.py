# Importing serializer base class from Django REST Framework
from rest_framework import serializers

# Importing built-in User model from Django
from django.contrib.auth.models import User

# Importing JWT refresh token generator
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore

# Importing Django's authenticate function to verify user credentials
from django.contrib.auth import authenticate


# Serializer to handle user registration
class RegisterSerializer(serializers.Serializer):
    # Define fields required for registration
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()

    # Validate registration data
    def validate(self, data):
        # Check if the username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('username is taken')
        
        return data

    # Create and return a new user instance
    def create(self, validated_data):
        # Create user with given data (except password for now)
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'].lower(),
        )
        # Set password securely (hashes the password)
        user.set_password(validated_data['password'])

        return validated_data


# Serializer to handle user login
class LoginSerializer(serializers.Serializer):
    # Define fields required for login
    username = serializers.CharField()
    password = serializers.CharField()

    # Validate login input
    def validate(self, data):
        # Check if the username exists in the database
        if not User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('account not found')
        
        return data

    # Custom method to get JWT tokens if login is successful
    def get_jwt_token(self, data):
        # Authenticate the user with provided credentials
        user = authenticate(username=data['username'], password=data['password'])

        # If authentication fails, return error message
        if not user:
            return {'message': 'invalid credentials', 'data': {}}
        
        # Generate refresh and access tokens
        refresh = RefreshToken.for_user(user)

        # Return success message with tokens
        return {
            'message': 'login success',
            'data': {
                'token': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }
        }
