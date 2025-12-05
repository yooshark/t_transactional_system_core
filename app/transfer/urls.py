from django.urls import path

from transfer.views import TransferAPIView

app_name = "transfer"

urlpatterns = [
    path("", TransferAPIView.as_view(), name="transfer"),
]
