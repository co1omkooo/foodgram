import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиетов в базу."""

    help = 'Импорт данных'
    model = Ingredient

    def handle(self, *args, **options):
        """Тело команды."""
        path = 'data/ingredients.json'
        file_name = os.path.basename(path)
        try:
            with open(path, 'r') as file:
                ingredients_to_create = [
                    self.model(**note) for note in file
                ]
                self.model.objects.bulk_create(ingredients_to_create)
                print(
                    f'Загрузка данных завершена\n'
                    f'В количестве {len(ingredients_to_create)} шт.'
                )
        except Exception as error:
            print(
                f'Ошибка при массовом добавлении.\n'
                f'Текст - {error}\n'
                f'Имя файла - {file_name}'
            )
