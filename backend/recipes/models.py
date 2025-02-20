from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from recipes.constans import (
    MAX_LENGTH_TAG_SLUG,
    MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_RECIPE_NAME,
    MAX_LENGTH_MEASUREMENT_UNIT,
    LIMIT_TEXT,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USER_NAME,
    MIN_COOKING_TIME,
    MIN_AMOUNT,
)


class User(AbstractUser):

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']
    USERNAME_FIELD = 'email'

    username = models.CharField(
        max_length=MAX_LENGTH_USER_NAME,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Ник',
    )
    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_USER_NAME,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_USER_NAME,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/avatar/',
        null=True,
        blank=True,
        default=None,
        verbose_name='Аватар',
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authors',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['follower', 'author']
            )
        ]

    def __str__(self):
        return f'{self.follower.username} подписан на {self.author.username}'


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        default_related_name = 'tags'
        ordering = ('name', )
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
        default_related_name = 'ingredients'
        ordering = ('name',)
        verbose_name = 'Продукт'
        verbose_name_plural = 'продукты'

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
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Продукты в рецепте',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления, мин.',
        validators=[MinValueValidator(MIN_COOKING_TIME)],
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-created_at',)

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
        verbose_name='Продукт'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_AMOUNT)],
        verbose_name='Мера'
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


class UserRecipeBase(models.Model):
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


class Favourite(UserRecipeBase):

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'favourites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'избранные'


class ShoppingCart(UserRecipeBase):

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'корзина покупок'
