from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet

from api.filters import RecipeFilter, IngredientFilter
from api.paginations import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    UserSerializer,
    IngredientSerializer,
    PostRecipeSerializer,
    UserSubscriberSerializer,
    TagSerializer,
    UserRecipesSerializer,
    AvatarSerializer
)
from api.utils import generate_shopping_list
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    Subscription,
    RecipeIngredient
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ('get',)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    http_method_names = ('get',)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = [AllowAny]
    pagination_class = None
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = PostRecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly,)
    pagination_class = LimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe_to_favorite_or_shopping_cart(
            self, request, model, pk
    ):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'DELETE':
            get_object_or_404(model, user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise ValidationError(
                {'detail': f'Рецепт {recipe.name} уже добавлен.'}
            )
        return Response(
            UserRecipesSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        methods=['GET'],
        detail=True,
        url_path='get-link',
    )
    def get_short_link(self, request, pk):
        if not Recipe.objects.filter(id=pk).exists():
            raise Http404(f'Рецепт с id={pk} не найден.')
        return Response(
            {'short-link': request.build_absolute_uri(
                reverse('recipes:redirect_short_link', args={pk})
            )},
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients_in_recipe = (
            RecipeIngredient.objects.filter(
                recipe__shopping_carts__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(
                total_amount=Sum('amount')
            ).order_by('ingredient__name')
        )
        recipes_in_cart = (
            Recipe.objects.filter(shopping_carts__user=request.user)
            .select_related('author')
            .distinct()
        )
        generate_shopping_list(
            ingredients_in_recipe, recipes_in_cart
        )
        return FileResponse(
            as_attachment=True,
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk):
        return self.add_recipe_to_favorite_or_shopping_cart(
            request, ShoppingCart, pk=pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
    )
    def favorite(self, request, pk):
        return self.add_recipe_to_favorite_or_shopping_cart(
            request, Favourite, pk=pk
        )


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitPagination

    @action(
        methods=['GET'],
        url_path='me',
        permission_classes=(IsAuthenticated,),
        detail=False,
    )
    def me(self, request):
        return Response(
            UserSerializer(request.user, context={'request': request}).data,
            status=status.HTTP_200_OK
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=kwargs['id'])
        if request.method == 'DELETE':
            get_object_or_404(
                Subscription, follower=request.user, author=author
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.user == author:
            raise ValidationError(
                {'detail': 'Нельзя подписаться на самого себя.'}
            )
        _, created = Subscription.objects.get_or_create(
            follower=request.user, author=author
        )
        if not created:
            raise ValidationError(
                {'detail': f'Вы уже подписаны на - {author}'}
            )
        serializer = UserSubscriberSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(authors__follower=request.user)
        page = self.paginate_queryset(queryset)
        return self.get_paginated_response(
            UserSubscriberSerializer(
                page, many=True, context={'request': request},
            ).data
        )

    @action(
        detail=False,
        methods=['PUT', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(user, data=request.data)
        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Аватар не найден', status=status.HTTP_404_NOT_FOUND
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )
