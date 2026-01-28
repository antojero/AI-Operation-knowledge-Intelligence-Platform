import uuid
from django.db import models
from django.conf import settings

class SystemLog(models.Model):
    class Level(models.TextChoices):
        INFO = 'INFO', 'Info'
        WARNING = 'WARNING', 'Warning'
        ERROR = 'ERROR', 'Error'
        CRITICAL = 'CRITICAL', 'Critical'

    class Component(models.TextChoices):
        BACKEND_CORE = 'BACKEND_CORE', 'Backend Core'
        BACKEND_AGENT = 'BACKEND_AGENT', 'Backend Agent'
        FRONTEND = 'FRONTEND', 'Frontend'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO)
    component = models.CharField(max_length=20, choices=Component.choices, default=Component.BACKEND_CORE)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: Link to User or Organization if applicable
    organization = models.ForeignKey('organizations.Organization', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.level}] {self.component}: {self.message[:50]}"
