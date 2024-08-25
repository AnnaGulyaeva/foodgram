from rest_framework import serializers

from subscriptions.models import Follow


def validate_follower(data):
    """Проверка корректности данных для подписки."""
    if data['user'] == data['following']:
        raise serializers.ValidationError(
            'Нельзя подписаться на самого себя!'
        )
    return data


def validate_follow(data):
    """Проверка уникальности подписки."""
    user = data['user']
    following = data['following']
    if Follow.objects.filter(
        user_id=user.id,
        following_id=following.id
    ):
        raise serializers.ValidationError(
            'Подписка уже есть!'
        )
    return data
