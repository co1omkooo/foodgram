from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from foodgram_backend.constans import (
    MAX_LENGTH_TAG_SLUG,
    MAX_LENGTH_SHORT_LINK,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_RECIPE_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    LIMIT_TEXT
)
from recipes.validators import validate_slug
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
        validators=[validate_slug],
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_INGREDIENT_NAME,
        verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASUREMENT_UNIT,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class Recipe(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name='Название',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    image = models.ImageField(
        upload_to='recipes/image/',
        verbose_name='Изображение',
    )
    text = models.TextField(
        verbose_name='Текст рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)],
    )
    created_at = models.DateTimeField(default=timezone.now)
    short_link = models.CharField(
        verbose_name='Короткая ссылка',
        max_length=MAX_LENGTH_SHORT_LINK,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name[:LIMIT_TEXT]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe',
            )
        ]
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Продукт в рецепте'
        verbose_name_plural = 'продукты в рецепте'

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class FavouriteShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_%(class)s',
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favourite(FavouriteShoppingCart):

    class Meta(FavouriteShoppingCart.Meta):
        default_related_name = 'favourites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'


class ShoppingCart(FavouriteShoppingCart):

    class Meta(FavouriteShoppingCart.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'корзина покупок'
