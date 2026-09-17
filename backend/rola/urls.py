"""rola URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from rest_framework.authtoken import views as drf_views
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
    path("register/activate", user_views.activate_user_view, name="activate-user"),
    path("password-reset", user_views.password_reset_view, name="password-reset"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
