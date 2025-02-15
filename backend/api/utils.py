from datetime import datetime
from django.db.models import Sum

from recipes.models import RecipeIngredient


def generate_shopping_list(user):
    ingredients_in_receipt = (
        RecipeIngredient.objects.filter(
            recipe__shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )
    )

    user_recipes = user.shopping_carts.values_list(
        'recipe__name', flat=True
    ).distinct()

    return '\n'.join([
        f'Список покупок для {user.username}. '
        f'Дата составления {datetime.now().strftime("%d.%m.%Y %H:%M")}:',
        "Продукты:",
        *[
            (f"{id_}. {ingredient_info['ingredient__name'].capitalize()}: "
             f"{ingredient_info['total_amount']} "
             f"{ingredient_info['ingredient__measurement_unit']}")
            for id_, ingredient_info in enumerate(
                ingredients_in_receipt,
                start=1
            )
        ],
        "Рецепты:",
        *[
            f"{recipe}"
            for recipe in user_recipes
        ],
    ])
