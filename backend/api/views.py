from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
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
from api.permissions import OwnerOrReadOnly
from api.serializers import (
    UserSerializer,
    IngredientSerializer,
    GetRecipeSerializer,
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
    serializer_class = GetRecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOrReadOnly,)
    pagination_class = LimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def handle_add_remove(self, request, model, **kwargs):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=kwargs['pk'])

        if request.method == 'DELETE':
            item = get_object_or_404(model, user=user, recipe=recipe)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if not created:
            raise ValidationError({"detail": "Рецепт уже добавлен."})

        return Response(
            UserRecipesSerializer(recipe).data, status=status.HTTP_201_CREATED
        )

    @action(
        methods=['GET'],
        detail=True,
        url_path='get-link',
        url_name='get-link'
    )
    def get_short_link(self, request, **kwargs):
        """Возвращает короткую ссылку на рецепт."""
        get_object_or_404(Recipe, pk=kwargs['pk'])
        rev_link = request.build_absolute_uri(f'/s/{kwargs["pk"]}')
        return Response(
            {'short-link': rev_link}, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        return FileResponse(
            generate_shopping_list(request.user),
            filename='shopping_list.txt',
            content_type='text/plain; charset=utf-8'
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, **kwargs):
        return self.handle_add_remove(request, ShoppingCart, **kwargs)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
    )
    def favorite(self, request, **kwargs):
        return self.handle_add_remove(request, Favourite, **kwargs)


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
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=kwargs['id'])

        if request.method == 'POST':
            if request.user == author:
                raise ValidationError(
                    {"detail": "Вы не можете подписаться на себя."}
                )

            _, created = Subscription.objects.get_or_create(
                follower=request.user, author=author
            )

            if not created:
                raise ValidationError(
                    {"detail": "Вы уже подписаны на этого пользователя."}
                )

            serializer = UserSubscriberSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        get_object_or_404(
            Subscription, follower=request.user, author=author
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(authors__follower=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscriberSerializer(
                page, many=True, context={'request': request},
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriberSerializer(
            page, many=True, context={'request': request},
        )
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['PUT', 'PATCH', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarSerializer(
            user, data=request.data, partial=True
        )

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
            {'avatar': user.avatar.url}, status=status.HTTP_200_OK
        )
