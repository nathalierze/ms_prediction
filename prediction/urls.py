from django.urls import path

from .views import SchuelerViewSet, SitzungssummaryViewSet

urlpatterns = [
    path('schueler', SchuelerViewSet.as_view({
        'get':'list',
        'post': 'create'
    })),
    path('schueler/<str:pk>', SchuelerViewSet.as_view({
        'get': 'retrieve',
        'post':'update'
    })),
    path('sitzungssummary', SitzungssummaryViewSet.as_view({
        'get':'list',
        'post': 'create'
    })),
    path('sitzungssummary/<str:pk>', SitzungssummaryViewSet.as_view({
        'post': 'getPrediction'
    }))

]