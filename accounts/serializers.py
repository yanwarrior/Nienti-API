from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError


class UserAfterLoginSerializer(serializers.ModelSerializer):
    """
    Must be read only
    """
    token = serializers.SerializerMethodField()

    def get_token(self, value):
        try:
            return f'Token {Token.objects.get(user=value).key}'
        except:
            return ''

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'token',
            'is_superuser',
            'is_active',
            'is_staff',
        ]


class SigninSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=200, required=True)
    password = serializers.CharField(max_length=200, required=True)

    def _create_safe_token(self, user):
        Token.objects.get_or_create(user=user)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Get user from username and chek is available
        users = User.objects.filter(username=username)
        if not users.exists():
            raise ValidationError('User tidak diketahui')

        if not users[0].check_password(password):
            raise ValidationError('Password tidak cocok')

        self._create_safe_token(users[0])

        return attrs

    def get_json(self):
        username = self.validated_data.get('username')
        user = User.objects.get(username=username)
        return UserAfterLoginSerializer(user).data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password']