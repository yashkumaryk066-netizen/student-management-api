import os
import django
import sys

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.contrib.auth.models import User
from student.models import UserProfile

def update_branding():
    print("--------------------------------------------------")
    print("Checking Admin Branding Setup...")
    
    # 1. Find Superuser
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No Superuser found in database.")
        return

    print(f"👤 Found Admin User: {admin.username}")

    # 2. Get or Create Profile
    try:
        profile, created = UserProfile.objects.get_or_create(user=admin)
        if created:
            print("⚠️  UserProfile was missing. Created new profile.")
            
        # 3. Check Institution Name
        current_name = profile.institution_name
        if current_name:
            print(f"✅ Institution Name is already set to: '{current_name}'")
            # Optional: Force update if it looks generic, but user asked 'if not set'
            if current_name.strip() == "":
                print("⚠️  Name is empty string.")
                update_it = True
            else:
                update_it = False
        else:
            print("⚠️  Institution Name is NOT set (None).")
            update_it = True
            
        # 4. Update if needed
        if update_it:
            target_name = "Y.S.M ADVANCE EDUCATION SYSTEM"
            target_type = "INSTITUTE"
            
            print(f"🔄 Setting Name to Premium Default: '{target_name}'")
            
            profile.institution_name = target_name
            profile.institution_type = target_type
            profile.role = 'ADMIN'
            profile.save()
            print("✅ Success! Branding has been updated.")
        else:
            print("👍 No changes needed.")

    except Exception as e:
        print(f"❌ Error updating profile: {e}")
        
    print("--------------------------------------------------")

if __name__ == "__main__":
    update_branding()
