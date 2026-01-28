import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization

User = get_user_model()

def seed():
    if not User.objects.filter(username='admin').exists():
        print("Creating admin user...")
        # Ensure default org exists
        org, _ = Organization.objects.get_or_create(
            slug='default-org', 
            defaults={'name': 'Default Organization'}
        )
        # Create superuser called admin
        u = User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        u.organization = org
        u.save()
        print("Admin user created (password: admin)")
    else:
        print("Admin user already exists.")

if __name__ == '__main__':
    seed()
