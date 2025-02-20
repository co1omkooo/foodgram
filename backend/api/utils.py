from datetime import datetime


def generate_shopping_list(ingredients, recipes):
    months_ru = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    current_month = datetime.now().month
    shopping_list = [
        'Список покупок ({}):'.format(months_ru[current_month - 1]), ''
        ]
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
