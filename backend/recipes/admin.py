from django.contrib import admin
from django.db.models import Count

from .models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Favourite, ShoppingCart)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('recipe',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


class InlineIngredients(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (InlineIngredients,)
    list_display = (
        'author', 'name', 'cooking_time', 'favourite_count', 'created_at',
    )
    search_fields = ('author', 'name',)
    list_filter = ('tags',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(fav_count=Count('favorites'))
        return queryset

    @admin.display(description='Кол-во в избранном')
    def favourite_count(self, obj):
        return obj.fav_count
