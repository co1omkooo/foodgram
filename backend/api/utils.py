from datetime import datetime


def generate_shopping_list(ingredients, recipes):
    current_date = datetime.now().strftime('%d.%m.%Y')
    shopping_list = ['Список покупок ({}):\n'.format(current_date)]
    shopping_list.extend(
        '{}. {} ({}) — {}'.format(
            i,
            item['ingredient__name'].capitalize(),
            item['ingredient__measurement_unit'],
            item['total_amount']
        )
        for i, item in enumerate(ingredients, start=1)
    )
    shopping_list.append('Рецепты:')
    shopping_list.extend(
        '- {} (автор: {})'.format(recipe.name, recipe.author.username)
        for recipe in recipes
    )
    return '\n'.join(shopping_list)
