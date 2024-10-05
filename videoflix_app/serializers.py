from videoflix_app.models import User, Video
from rest_framework import serializers
from django.contrib.auth import authenticate

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
              

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model. Handles user creation and serialization
    of user data, including password handling.

    Fields:
            
    id: The user's ID (auto-generated).
    username: The username of the user.
    email: The email address of the user.
    password: The password of the user (write-only).
    """
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
            """
            Create a new user instance with the validated data.
            The password is hashed before saving the user.
            """
            user = User  (
                username=validated_data['username'],
                email=validated_data['email'],
            )
            user.set_password(validated_data['password'])
            user.save()
            return user

    class Meta:
            model = User
            fields = ('id', 'username', 'email', 'password')              
            
class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Validates the provided email and password,
    and authenticates the user if the credentials are correct.

    Fields:
            
    email: The email address of the user.
    password: The password of the user."""
    email = serializers.EmailField()
    password = serializers.CharField()
    remember = serializers.BooleanField(required=False)

    def validate(self, data):
        """
        Validate the provided email and password. Authenticate the user
        and raise an error if the credentials are invalid.
        """
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # print(email, password)
            user = authenticate(username=email, password=password)
            print(user)
            if not user:
                raise serializers.ValidationError("Invalid login credentials")
        else:
            raise serializers.ValidationError("Both fields must be filled")

        data['user'] = user
        return data        