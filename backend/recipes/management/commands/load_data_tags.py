from load_data import BaseImportCommand

from recipes.models import Tag


class Command(BaseImportCommand):
    """Команда для импорта тегов в базу."""

    model = Tag
    data_file = 'data/tags.json'
