from django.contrib import admin
from django.urls import path, include, re_path

from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework.routers import DefaultRouter
from constructor.views import (
    CategoryViewSet,
    ServiceViewSet,
    ServiceImageViewSet,
    PartyConstructorViewSet,
    OrderViewSet, PartyConstructorDetailView
)

# Swagger schema view setup
schema_view = get_schema_view(
    openapi.Info(
        title="Tantana API",
        default_version='v1',
        description="API documentation for Tantana project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@tantana.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-images', ServiceImageViewSet, basename='serviceimage')
router.register(r'party-constructors', PartyConstructorViewSet, basename='partyconstructor')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'detail', PartyConstructorDetailView, basename='detail')

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path('users/', include('user.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
