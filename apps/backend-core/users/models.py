import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'
        VIEWER = 'VIEWER', 'Viewer'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'organizations.Organization', 
        on_delete=models.CASCADE, 
        related_name='users',
        null=True, # Allow null for superusers/orphan users initially
        blank=True
    )
    role = models.CharField(
        max_length=20, 
        choices=Roles.choices, 
        default=Roles.MEMBER
    )

    def __str__(self):
        return self.username
