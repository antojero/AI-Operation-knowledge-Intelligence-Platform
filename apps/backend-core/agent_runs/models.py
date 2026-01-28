import uuid
from django.db import models
from django.conf import settings

class AgentRun(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'QUEUED', 'Queued'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='agent_runs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agent_runs')
    
    agent_type = models.CharField(max_length=50, default='RESEARCHER')
    input_params = models.JSONField(default=dict)
    output_result = models.JSONField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    error_message = models.TextField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0.000000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent_type} - {self.id}"

class RunStep(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(AgentRun, on_delete=models.CASCADE, related_name='steps')
    step_type = models.CharField(max_length=50) # e.g., 'tool_call', 'reasoning'
    content = models.JSONField()
    usage_tokens = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
