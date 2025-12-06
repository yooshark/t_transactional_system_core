from django.contrib import admin
from django.urls import path, include

api = [
    path("transfer/", include("transfer.urls", namespace="transfer")),
]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api)),
]
