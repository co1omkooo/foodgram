import json
import os
from typing import Type


from django.core.management.base import BaseCommand
from django.db import models


from recipes.models import Ingredient, Tag


class BaseImportCommand(BaseCommand):
    """Базовый класс для импорта данных."""

    help = 'Импорт данных'
    model: Type[models.Model]
    data_file: str
    item_name: str

    def handle(self, *args, **options):
        """Тело команды."""
        path = self.data_file
        file_name = os.path.basename(path)
        try:
            with open(path, 'r', encoding='UTF-8') as file:
                created_count = 0
                for note in json.load(file):
                    _, created = self.model.objects.get_or_create(**note)
                    if created:
                        created_count += 1
                print(
                    f'Загрузка данных завершена\n'
                    f'Добавлено {created_count} новых {self.item_name}.'
                )
        except Exception as error:
            print(
                f'Ошибка при массовом добавлении.\n'
                f'Текст - {error}\n'
                f'Имя файла - {file_name}'
            )


class Command(BaseImportCommand):
    """Команда для импорта ингредиентов в базу."""

    model = Ingredient
    data_file = 'data/ingredients.json'
    item_name = 'ингредиентов'

# Перед запуском изменить имя класса CommandTag на Command


class CommandTag(BaseImportCommand):
    """Команда для импорта тегов в базу."""

    model = Tag
    data_file = 'data/tags.json'
    item_name = 'тегов'
