from django.contrib.auth import authenticate

from rest_framework import serializers

from videoflix_app.models import User, Video



class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
              

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    def create(self, validated_data):
        """
        Creates a new user with the given validated_data.

        :param validated_data: A dictionary of validated data from the request
        :return: The newly created user
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'remember')            
            
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    remember = serializers.BooleanField(required=False)

    def validate(self, data):
        """
        Validates the given data for a login request.

        :param data: A dictionary of the given data
        :return: The validated data with the user object added
        :raises: serializers.ValidationError if the credentials are invalid
        :raises: serializers.ValidationError if either email or password is empty
        """
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid login credentials")
        else:
            raise serializers.ValidationError("Both fields must be filled")

        data['user'] = user
        return data        

class ResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)