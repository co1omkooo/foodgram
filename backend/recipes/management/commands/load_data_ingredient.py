from .load_data import BaseImportCommand

from recipes.models import Ingredient


class Command(BaseImportCommand):
    """Команда для импорта ингредиентов в базу."""

    model = Ingredient
    data_file = 'data/ingredients.json'
