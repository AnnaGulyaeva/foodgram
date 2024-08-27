import re

from rest_framework import serializers

from accounts.constants import (
    PASSWORD_MAX_LENGTH,
    USERNAME_PATTERN,
    USERNAME_RESERVED
)
from accounts.models import User
from foodgram_api.fields import Base64ImageField


class AvatarCreateDeleteSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и изменения аватара."""

    avatar = Base64ImageField(
        required=True,
        allow_null=True
    )
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настройки сериализатора."""

        model = User
        fields = (
            'avatar',
            'avatar_url'
        )

    def get_avatar_url(self, obj):
        """Получение ссылки на автар."""
        if obj.avatar:
            return obj.avatar.url

    def to_representation(self, instance):
        """Изменение возвращаемых данных."""
        representation = super().to_representation(instance)
        representation['avatar'] = representation['avatar_url']
        representation.pop('avatar_url')
        return representation


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя."""

    password = serializers.CharField(write_only=True)

    class Meta:
        """Дополнительные настройки сериализатора."""

        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )

    def validate_username(self, value):
        """Проверка корректности username."""
        if (value == USERNAME_RESERVED
                or not re.match(USERNAME_PATTERN, value)):
            raise serializers.ValidationError(
                'Выберете другое имя пользователя!'
            )
        return value

    def create(self, validated_data):
        """Добавление пароля в БД."""
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UsersGetListSerializer(
    AvatarCreateDeleteSerializer,
    serializers.ModelSerializer
):
    """Сериализатор для получения профиля или списка профилей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Дополнительные настройки сериализатора."""

        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
            'avatar_url'
        )

    def get_is_subscribed(self, obj):
        """Проверка подписки на данного пользователя."""
        return obj.following.filter(
            user_id=self.context['request'].user.id
        ).exists()


class SetPasswordSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения пароля."""

    current_password = serializers.CharField(
        write_only=True,
        max_length=PASSWORD_MAX_LENGTH
    )
    new_password = serializers.CharField(
        write_only=True,
        max_length=PASSWORD_MAX_LENGTH
    )

    class Meta:
        """Дополнительные настройки сериализатора."""

        model = User
        fields = (
            'current_password',
            'new_password'
        )

    def validate(self, attrs):
        """Проверка старого пароля."""
        user = self.context['request'].user
        if not user.check_password(attrs['current_password']):
            raise serializers.ValidationError("Старый пароль неверен.")
        return attrs

    def save(self):
        """Сохранение нового пароля."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
