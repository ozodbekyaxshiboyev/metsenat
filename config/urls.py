from django.contrib import admin
from django.urls import path,include
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title = "Metsenat REST API",
        default_version="v0",
        description="Bu talabalar va homiylar uchun ajoyib platforma",
        contact=openapi.Contact("")
    ),
    public=True,
    permission_classes=(AllowAny,)
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apiv0/', include('metsenat.urls')),
    path('swagger/', schema_view.with_ui('swagger',cache_timeout=0),name='swagger-docs'),
    path('redocs/', schema_view.with_ui('redoc',cache_timeout=0),name='redoc-docs')
]
