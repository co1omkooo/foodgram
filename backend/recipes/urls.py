from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path(
        's/<str:short_id>/',
        views.redirect_short_link,
        name='redirect_short_link'
    ),
]
