def generate_shopping_list(ingredients):
    shopping_list = []
    for item in ingredients:
        name = item['ingredient__name']
        unit = item['ingredient__measurement_unit']
        total_amount = item['total_amount']
        shopping_list.append(f"{name} ({unit}) — {total_amount}")
    shopping_list_text = "\n".join(shopping_list)
    return shopping_list_text
