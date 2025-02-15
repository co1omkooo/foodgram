import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Команда для импорта ингредиетов в базу."""

    help = 'Импорт ингредиентов'

    def handle(self, *args, **options):
        """Тело команды."""
        with open('data/ingredients.json', 'r') as file:
            ingredients_to_create = []
            for note in json.load(file):
                try:
                    ingredients_to_create.append(Ingredient(**note))
                    print(f"{note['name']} в базе")
                except Exception as error:
                    print(
                        f"Ошибка добавления {note['name']}.\n"
                        f"Текст - {error}"
                    )
            try:
                Ingredient.objects.bulk_create(ingredients_to_create)
                print('Загрузка ингредиентов завершена')
            except Exception as error:
                print(
                    f"Ошибка при массовом добавлении.\n"
                    f"Текст - {error}"
                )
