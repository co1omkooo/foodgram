from django.urls import path

from recipes.views import redirect_short_link

app_name = 'recipes'


urlpatterns = [
    path(
        's/<int:pk>/',
        redirect_short_link,
        name='redirect_short_link'
    ),
]
