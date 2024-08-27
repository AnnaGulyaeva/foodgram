# Generated by Django 3.2.3 on 2024-08-27 08:54

import accounts.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_delete_follow'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='user',
            name='unique_user',
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(db_index=True, max_length=150, unique=True, validators=[accounts.validators.username_validator], verbose_name='Имя пользователя'),
        ),
    ]
