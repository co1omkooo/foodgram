from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.serializers import UserRecipesSerializer
from recipes.models import Recipe


class AddRemoveMixin:
    def handle_add_remove(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'DELETE':
            try:
                item = model.objects.get(user=user, recipe=recipe)
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except model.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        _, created = model.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = UserRecipesSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
