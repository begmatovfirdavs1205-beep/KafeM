from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from core.admin_site import cafe_admin_site

urlpatterns = [
    path("admin/", cafe_admin_site.urls),
    path("", include("core.urls")),
    path("menu/", include("menu.urls")),
    path("orders/", include("orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
