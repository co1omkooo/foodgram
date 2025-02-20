from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Subscription,
)

User = get_user_model()

admin.site.unregister(Group)


class RecipesCountMixin:
    @admin.display(description='Рецепты')
    def recipes_count(self, object):
        return object.recipes.count()


@admin.register(User)
class UserAdmin(UserAdmin, RecipesCountMixin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительные поля',
         {'fields': ('avatar',)}),
    )
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'avatar_preview',
        'subscription_count',
        'subscriber_count',
        'recipes_count',
    )
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_preview(self, user):
        if user.avatar:
            return (
                format_html(
                    '<img src="{}" width="50" height="50"; />',
                    user.avatar.url
                )
            )
        return 'Нет аватара'

    @admin.display(description='Подписки')
    def subscription_count(self, user):
        return user.followers.count()

    @admin.display(description='Подписчики')
    def subscriber_count(self, user):
        return user.authors.count()


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'follower', 'author')
    list_editable = ('follower', 'author')
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin, RecipesCountMixin):
    list_display = ('name', 'slug', 'recipes_count')
    search_fields = ('name', 'slug',)


@admin.register(Favourite, ShoppingCart)
class UserRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user',)
    list_filter = ('recipe',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin, RecipesCountMixin):
    list_display = ('id', 'name', 'measurement_unit', 'recipes_count',)
    search_fields = ('name', 'measurement_unit',)
    list_filter = ('measurement_unit',)


@admin.register(RecipeIngredient)
class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


class InlineIngredients(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (InlineIngredients,)
    list_display = (
        'name',
        'cooking_time_display',
        'author',
        'tags_display',
        'favourite_count',
        'ingredients_display',
        'image_display',
    )
    search_fields = ('author', 'name',)
    list_filter = ('tags', 'author',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(fav_count=Count('favourites'))
        return queryset

    @admin.display(description='Время (мин)')
    def cooking_time_display(self, recipe):
        return recipe.cooking_time

    @admin.display(description='Теги')
    @mark_safe
    def tags_display(self, recipe):
        return '<br>'.join(map(str, recipe.tags.all()))

    @admin.display(description='Картинка')
    @mark_safe
    def image_display(self, recipe):
        return f'<img src="{recipe.image.url}" width="50" height="50">'

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_display(self, recipe):
        return '<br>'.join(
            f'{recipe_ingredients.ingredient.name}, '
            f'{recipe_ingredients.ingredient.measurement_unit}, '
            f'{recipe_ingredients.amount}'
            for recipe_ingredients in
            recipe.recipe_ingredients.all()
        )

    @admin.display(description='В избранном')
    def favourite_count(self, favourite):
        return favourite.fav_count
