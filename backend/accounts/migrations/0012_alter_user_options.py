# Generated by Django 3.2.3 on 2024-08-29 08:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_auto_20240827_0854'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('username',), 'verbose_name': 'пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
    ]
