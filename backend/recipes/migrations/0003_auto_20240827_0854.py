# Generated by Django 3.2.3 on 2024-08-27 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20240825_1903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='description',
            field=models.TextField(verbose_name='Текстовое описание'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(default=None, max_length=32, verbose_name='Слаг'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient'),
        ),
    ]
