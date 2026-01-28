from rest_framework import viewsets, permissions
from .models import Organization
from .serializers import OrganizationSerializer

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show org usually? Or admin only? 
        # For Phase 0/Foundation, let's keep it simple: Authenticated users can see their own org or all if admin.
        # But for now, since we have no complex RLS yet, let's just return all.
        return Organization.objects.all()
    
    def perform_create(self, serializer):
        serializer.save()
