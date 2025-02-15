from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer as DjoserUserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Tag,
    Ingredient,
    RecipeIngredient,
    Recipe,
    Subscription
)

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    avatar = Base64ImageField()
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed'
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

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserRecipesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        exclude = ['created_at']

    def get_is_in_favorite(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.favourites.filter(recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and request.user.shopping_carts.filter(recipe=obj).exists())


class GetRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, required=True, source='recipe_ingredients'
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

    def validate_cooking_time(self, cooking_time):
        if not cooking_time:
            raise serializers.ValidationError(
                'Обязательное поле "cooking_time".'
            )
        return cooking_time

    def validate(self, attrs):
        tags = attrs.get('tags')
        ingredients = attrs.get('recipe_ingredients')
        image = attrs.get('image')
        if not image:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле image'
            )
        if not tags:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле tags'
            )
        if not ingredients:
            raise serializers.ValidationError(
                'Отсутствует обязательное поле ingredients'
            )
        ingredients_ids = [
            ingredient.get('ingredient').id for ingredient in ingredients
        ]
        if len(set(ingredients_ids)) != len(ingredients):
            raise serializers.ValidationError(
                'Ингридиенты должны быть уникальными'
            )
        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                'Тэги должны быть уникальными'
            )
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
        recipe = Recipe.objects.create(**validated_data)
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
            context={'request': self.context.get('request')}
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
        request = self.context.get('request')
        limit = int(request.GET.get('recipes_limit', 10 ** 10))
        recipes = user.recipes.all()[:limit]
        return UserRecipesSerializer(recipes, many=True).data

    def get_recipes_count(self, user):
        return user.recipes.count()


class SubscriptionsSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['subscriptions']

    def get_subscriptions(self, obj):
        request = self.context['request']
        user = request.user
        subscriptions = Subscription.objects.filter(follower=user)
        return UserSubscriberSerializer(
            [subscription.following for subscription in subscriptions],
            many=True,
            context={'request': request}
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar')
        if avatar is None:
            raise serializers.ValidationError('Необходимо загрузить аватар.')
        instance.avatar = avatar
        instance.save()
        return instance
