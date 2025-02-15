from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe

from .models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
    Subscription,
    User
)


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'first_name',
        'last_name',
        'email',
        'avatar',
        'subscription_count',
        'subscriber_count',
        'recipe_count'
    )
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'

    @admin.display(description='Автар')
    @mark_safe
    def get_avatar(self, user):
        return f'<img src="{user.image.url}" width="50" height="50">'

    @admin.display(description='Подписки')
    def subscription_count(self, user):
        return user.followers.count()

    @admin.display(description='Подписчики')
    def subscriber_count(self, user):
        return user.authors.count()

    @admin.display(description='Рецепты')
    def recipe_count(self, user):
        return user.recipes.count()


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'follower', 'author')
    list_editable = ('follower', 'author')
    empty_value_display = '-пусто-'


class RecipesCountMixin:
    @admin.display(description='Рецепты')
    def recipes_count(self, object):
        return object.recipes.count()


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
    list_filter = ('tags',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(fav_count=Count('favourites'))
        return queryset

    @admin.display(description='Время (мин)')
    def cooking_time_display(self, receipt):
        return receipt.cooking_time

    @admin.display(description='Теги')
    @mark_safe
    def tags_display(self, receipt):
        return '<br>'.join(map(str, receipt.tags.all()))

    @admin.display(description='Картинка')
    @mark_safe
    def image_display(self, receipt):
        return f'<img src="{receipt.image.url}" width="50" height="50">'

    @admin.display(description='Продукты')
    @mark_safe
    def ingredients_display(self, receipt):
        return '<br>'.join(
            [
                f'{ingredient_in_receipt.ingredient.name}, '
                f'{ingredient_in_receipt.ingredient.measurement_unit}, '
                f'{ingredient_in_receipt.amount}'
                for ingredient_in_receipt in
                receipt.ingredients_in_receipts.all()
            ]
        )

    @admin.display(description='Кол-во в избранном')
    def favourite_count(self, favourite):
        return favourite.fav_count
