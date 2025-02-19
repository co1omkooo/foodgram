from datetime import datetime


def generate_shopping_list(ingredients, recipes):
    current_date = datetime.now().strftime("%d.%m.%Y")
    shopping_list = ["Список покупок ({}):\n".format(current_date)]
    shopping_list.extend(
        "{}. {} ({}) — {}".format(
            i + 1,
            item['ingredient__name'].capitalize(),
            item['ingredient__measurement_unit'],
            item['total_amount']
        )
        for i, item in enumerate(ingredients)
    )
    shopping_list.append("\nРецепты:")
    shopping_list.extend(
        "- {} (автор: {})".format(recipe['name'], recipe['author'])
        for recipe in recipes
    )
    shopping_list_text = "\n".join(shopping_list)
    return shopping_list_text
