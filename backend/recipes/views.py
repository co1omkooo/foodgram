from django.shortcuts import redirect
from django.http import Http404

from .models import Recipe


def redirect_short_link(request, pk):
    """Перенаправляет на полный URL рецепта."""
    if not Recipe.objects.filter(id=pk).exists():
        raise Http404(f'Рецепт c id {pk} не найден.')
    return redirect(f'/recipes/{pk}/')
