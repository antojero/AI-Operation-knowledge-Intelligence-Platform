from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import AgentRun, RunStep
from .serializers import AgentRunSerializer, RunStepSerializer
from django.conf import settings
import os

class IsInternalServiceOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        internal_secret = request.headers.get('X-Internal-Secret')
        if internal_secret and internal_secret == os.environ.get('INTERNAL_SERVICE_SECRET', 'supersecret'):
            return True
        return bool(request.user and request.user.is_authenticated)

class AgentRunViewSet(viewsets.ModelViewSet):
    queryset = AgentRun.objects.all()
    serializer_class = AgentRunSerializer
    permission_classes = [IsInternalServiceOrAuthenticated]

    def get_queryset(self):
        # Internal service sees all, users see theirs
        internal_secret = self.request.headers.get('X-Internal-Secret')
        if internal_secret and internal_secret == os.environ.get('INTERNAL_SERVICE_SECRET', 'supersecret'):
             return AgentRun.objects.all()
        return AgentRun.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        internal_secret = self.request.headers.get('X-Internal-Secret')
        if internal_secret and internal_secret == os.environ.get('INTERNAL_SERVICE_SECRET', 'supersecret'):
             # Create without specific user context, or assign a default system user?
             # For now, require 'user_id' in body if internal, or allow null if model allows (model has user FK)
             # Let's assume frontend passes user_id or we use a system user. 
             # Actually, simpler: just save. Serializer validation will check required fields.
             serializer.save()
        else:
             serializer.save(user=self.request.user, organization=self.request.user.organization)

class RunStepViewSet(viewsets.ModelViewSet): # Changed to ModelViewSet to allow creation
    queryset = RunStep.objects.all()
    serializer_class = RunStepSerializer
    permission_classes = [IsInternalServiceOrAuthenticated]

    def get_queryset(self):
        internal_secret = self.request.headers.get('X-Internal-Secret')
        if internal_secret and internal_secret == os.environ.get('INTERNAL_SERVICE_SECRET', 'supersecret'):
             return RunStep.objects.all()
        return RunStep.objects.filter(run__user=self.request.user)
