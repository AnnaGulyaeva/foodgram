import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm

from recipes.management.commands.constants import PATH
from recipes.models import Tag


class Command(BaseCommand):
    """Добавление ингредиентов в базу данных."""

    def handle(self, *args, **options):
        csv_path = os.path.join(
            settings.BASE_DIR,
            PATH,
            'tags.csv'
        )
        csv_file = open(csv_path, 'r', encoding='utf-8')
        total_lines = sum(1 for _ in csv.reader(csv_file, delimiter=','))
        csv_file = open(csv_path, 'r', encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in tqdm(csv_reader, total=total_lines, ncols=80):
            ingrediant, created = Tag.objects.get_or_create(
                name=row[0],
                slug=row[1]
            )
        self.stdout.write(self.style.SUCCESS('Теги добавлены в базу данных'))
