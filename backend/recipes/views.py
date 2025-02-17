from django.shortcuts import redirect
from django.http import Http404

from .models import Recipe


def redirect_short_link(request, pk):
    """Перенаправляет на полный URL рецепта."""
    if not Recipe.objects.filter(id=pk).exists():
        raise Http404('Рецепт не найден.')
    return redirect('api:recipes-detail', kwargs={'pk': pk})
