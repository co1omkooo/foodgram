from django.shortcuts import get_object_or_404, redirect
from .models import ShortLink


def redirect_short_link(request, short_id):
    recipe = get_object_or_404(ShortLink, short_link=short_id)
    return redirect(f'/recipes/{recipe.id}')
