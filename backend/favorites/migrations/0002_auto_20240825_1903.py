# Generated by Django 3.2.3 on 2024-08-25 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20240825_1903'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('favorites', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'default_related_name': 'favorites', 'verbose_name': 'избранное', 'verbose_name_plural': 'Избранные'},
        ),
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
