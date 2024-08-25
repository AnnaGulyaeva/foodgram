import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    """Добавление ингредиентов в базу данных."""

    def handle(self, *args, **options):
        csv_path = os.path.join(
            settings.BASE_DIR,
            'recipes/management/commands/',
            'tags.csv'
        )
        csv_file = open(csv_path, 'r', encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            ingrediant, created = Tag.objects.get_or_create(
                name=row[0],
                slug=row[1]
            )
        print('tags - OK')
