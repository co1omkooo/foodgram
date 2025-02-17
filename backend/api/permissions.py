from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, recipe):
        return (
            request.method in permissions.SAFE_METHODS
            or recipe.author == request.user
        )
