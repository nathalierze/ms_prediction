from django.urls import path

from .views import SchuelerViewSet, SitzungssummaryViewSet

urlpatterns = [
    path("schueler/<str:pk>", SchuelerViewSet.as_view({"post": "get_next_sentence"})),
    path(
        "sitzungssummary/<str:pk>",
        SitzungssummaryViewSet.as_view({"post": "get_prediction"}),
    ),
]
