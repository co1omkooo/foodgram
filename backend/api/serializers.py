from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Tag,
    Ingredient,
    RecipeIngredient,
    Recipe,
)
from recipes.constans import MIN_AMOUNT, MIN_COOKING_TIME

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField(
        required=False,
        allow_null=True
    )
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = tuple(
            field for field in DjoserUserSerializer.Meta.fields
            if field != 'password'
        ) + (
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, followers):
        user = self.context.get('request').user
        return user.is_authenticated and user.followers.filter(
            follower=followers
        ).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(
        min_value=MIN_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для получения рецепта."""

    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipe_ingredients'
    )
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_in_favorite'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        exclude = ('created_at',)

    def get_is_in_favorite(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favourites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.shopping_carts.filter(recipe=obj).exists())


class PostRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, required=True, source='recipe_ingredients'
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def dublicate_ingredients_tags(self, objs):

        if len(set(objs)) != len(objs):
            raise serializers.ValidationError(
                f'Продыкты не должны дублироваться - {objs}'
            )

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('recipe_ingredients')
        image = attrs.get('image')
        if not image:
            raise serializers.ValidationError(
                'Поле image обязательное'
            )
        if not tags:
            raise serializers.ValidationError(
                'Поле tags обязательное'
            )
        if not ingredients:
            raise serializers.ValidationError(
                'Поле ingredients обязательное'
            )
        ingredients_ids = [
            ingredient.get('ingredient').id for ingredient in ingredients
        ]
        self.dublicate_ingredients_tags(ingredients_ids)
        self.dublicate_ingredients_tags(tags)

        return attrs

    def recipe_ingredients_create(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                **ingredient_data
            )
            for ingredient_data in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        recipe = super().create(validated_data)
        recipe.tags.set(tags_data)
        self.recipe_ingredients_create(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('recipe_ingredients')
        instance.tags.set(tags_data)
        instance.recipe_ingredients.all().delete()
        self.recipe_ingredients_create(instance, ingredients_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(
            instance,
            context=self.context
        ).data


class UserSubscriberSerializer(UserSerializer):
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True
    )
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            *UserSerializer.Meta.fields,
            'recipes_count',
            'recipes',
        )

    def get_recipes(self, user):
        return UserRecipesSerializer(
            user.recipes.all()[
                :int(self.context.get('request').GET.get(
                    'recipes_limit', 10 ** 10
                ))
            ],
            many=True
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)
