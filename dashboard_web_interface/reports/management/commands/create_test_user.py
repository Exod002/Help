from django.core.management.base import BaseCommand
from reports.models import CustomUser
from django.utils import timezone

class Command(BaseCommand):
    help = 'Creates a test user for development'

    def handle(self, *args, **options):
        # Create test user
        user = CustomUser.objects.create_user(
            email='admin@apo.com.tn',
            username='admin',
            password='admin123',
            department='IT',
            is_verified=True,
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created test user'))
        self.stdout.write(f'Email: {user.email}')
        self.stdout.write('Password: admin123') 