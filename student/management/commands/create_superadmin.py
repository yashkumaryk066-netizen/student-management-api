from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import UserProfile

class Command(BaseCommand):
    help = 'Create a super admin with lifetime access'

    def handle(self, *args, **options):
        username = 'yash.kumar'
        email = 'yash.kumar@yourdomain.com'
        password = 'Ysonm@12'
        
        # Check if super admin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'Super admin "{username}" already exists!'))
            user = User.objects.get(username=username)
            # Update password if needed
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS('✅ Super Admin Password Updated!'))
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
        self.stdout.write(self.style.WARNING('⚠️  Keep these credentials secure!'))
