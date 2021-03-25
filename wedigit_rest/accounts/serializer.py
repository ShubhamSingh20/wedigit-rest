from typing import OrderedDict
from accounts.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='slug')
    last_name = serializers.CharField(required=False)
    first_name = serializers.CharField()
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(validators=[
        UniqueValidator(queryset=User.objects.all())
    ])

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 
            'last_name', 'password'
        ]
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def create(self, validated_data) -> User:
        user : User = super().create(validated_data)
        if password := validated_data.get('password', False):
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data) -> User:
        user : User = super().update(instance, validated_data)
        if password := validated_data.get('password', False):
            user.set_password(password)
            user.save()
        return user
