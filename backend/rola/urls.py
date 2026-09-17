"""Route the versioned API and Django administration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from drf_user import views as user_views
from rolca.urls import route_lists

router = SimpleRouter(trailing_slash=False)
router.register("user", user_views.UserViewSet, basename="user")
for route_list in route_lists:
    for prefix, viewset in route_list:
        router.register(prefix, viewset, basename=prefix.replace("/", "-"))

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api/v1/user/login", user_views.LoginView.as_view(), name="login"),
    path("api/v1/", include(router.urls)),
    path("core/", include("rolca.core.urls", namespace="rolca-core")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
