from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.mixins import AddRemoveMixin
from api.paginations import LimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    AvatarUserSerializer,
    CreateUserSerializer,
    UserSetPasswordSerializer,
    IngredientSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)
from recipes.models import (
    Favourite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = AvatarUserSerializer
    pagination_class = LimitPagination

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return User.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateUserSerializer
        if self.action == 'set_password':
            return UserSetPasswordSerializer
        return AvatarUserSerializer

    @action(detail=False, methods=['POST'])
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['PUT', 'PATCH', 'DELETE'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request):
        user = request.user
        serializer = AvatarUserSerializer(
            user, data=request.data,
            partial=True
        )

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Аватар не найден',
                status=status.HTTP_404_NOT_FOUND
            )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'avatar': user.avatar.url},
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, methods=['POST', 'DELETE'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response(
                'Вы не можете подписаться на себя.',
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=user,
                author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                'Вы не подписаны на этого пользователя',
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, created = Subscription.objects.get_or_create(
            user=user,
            author=author
        )
        if created:
            recipes_limit = request.query_params.get('recipes_limit')
            serializer = SubscriptionSerializer(
                author,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            'Вы уже подписаны на этого пользователя',
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
            detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribed_to__user=user)
        recipes_limit = request.query_params.get('recipes_limit')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request, 'recipes_limit': recipes_limit},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
        )
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet, AddRemoveMixin):
    queryset = Recipe.objects.all().order_by('-created_at')
    serializer_class = RecipeSerializer
    pagination_class = LimitPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ['tags__slug']

    def get_permissions(self):
        if self.action in [
            'create',
            'update',
            'partial_update',
            'destroy',
            'favorite',
            'download_shopping_cart',
            'shopping_cart'
        ]:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if author:
            queryset = queryset.filter(author__id=author)
        return queryset.order_by('id')

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = self.get_object()
        short_link = recipe.short_link
        short_url = request.build_absolute_uri(f'/s/{short_link}')
        return Response({'short-link': short_url},
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return self.handle_add_remove(request, pk, ShoppingCart)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(content_type='text/plain')

        shopping_cart = ShoppingCart.objects.filter(user=user).values_list(
            'recipe', flat=True
        )

        ingredients_sum = (
            RecipeIngredient.objects.filter(recipe__in=shopping_cart)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        response.write('Список покупок:\n\n'.encode('utf-8'))
        for index, item in enumerate(ingredients_sum, start=1):
            line = (
                f"{index}. {item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}\n"
            )
            response.write(line.encode('utf-8'))
        return response

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        return self.handle_add_remove(request, pk, Favourite)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


def redirect_short_link(request, short_id):
    recipe = get_object_or_404(Recipe, short_link=short_id)
    return redirect(f'/recipes/{recipe.id}')
