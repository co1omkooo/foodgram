from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

from api.views import redirect_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('s/<str:short_id>/', redirect_short_link, name='redirect_short_link'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
