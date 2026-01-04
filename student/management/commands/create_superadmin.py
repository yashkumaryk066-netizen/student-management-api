from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import UserProfile

class Command(BaseCommand):
    help = 'Create a super admin with lifetime access'

    def handle(self, *args, **options):
        username = 'superadmin'
        email = 'admin@yourdomain.com'
        password = 'Admin@123456'  # Change this after first login
        
        # Check if super admin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Super admin "{username}" already exists!'))
            return
        
        # Create super admin user
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Create profile with lifetime access
        UserProfile.objects.create(
            user=user,
            role='SUPER_ADMIN',
            institution_type='ALL',  # Access to all types
            phone='',
            subscription_expiry=None  # No expiry = lifetime access
        )
        
        self.stdout.write(self.style.SUCCESS('✅ Super Admin Created Successfully!'))
        self.stdout.write(self.style.SUCCESS(f'   Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'   Email: {email}'))
        self.stdout.write(self.style.SUCCESS(f'   Password: {password}'))
        self.stdout.write(self.style.SUCCESS(f'   Access: Lifetime (No expiry)'))
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANT: Change password after first login!'))
