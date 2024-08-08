from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParticipantViewSet, TournamentViewSet, RoundViewSet, MatchViewSet

router = DefaultRouter()
router.register(r'participants', ParticipantViewSet, basename='participants')
router.register(r'tournaments', TournamentViewSet)
router.register(r'rounds', RoundViewSet)
router.register(r'matches', MatchViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
