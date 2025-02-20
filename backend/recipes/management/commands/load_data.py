import json
import os
from typing import Type

from django.core.management.base import BaseCommand
from django.db import models


class BaseImportCommand(BaseCommand):
    """Базовый класс для импорта данных."""

    help = 'Импорт данных'
    model: Type[models.Model]
    data_file: str

    def handle(self, *args, **options):
        """Тело команды."""
        path = self.data_file
        file_name = os.path.basename(path)
        try:
            with open(path, 'r', encoding='UTF-8') as file:
                initial_count = self.model.objects.count()
                new_notes = [
                    self.model(**note) for note in json.load(file)
                ]
                self.model.objects.bulk_create(
                    new_notes, ignore_conflicts=True
                )
                final_count = self.model.objects.count()
                created_count = final_count - initial_count
                print(
                    f'Загрузка данных завершена\n'
                    f'Добавлено {created_count} новых.'
                )
        except Exception as error:
            print(
                f'Ошибка при массовом добавлении.\n'
                f'Текст - {error}\n'
                f'Имя файла - {file_name}'
            )
