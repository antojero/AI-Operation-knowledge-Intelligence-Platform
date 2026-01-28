from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgentRunViewSet, RunStepViewSet

router = DefaultRouter()
router.register(r'runs', AgentRunViewSet)
router.register(r'steps', RunStepViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
