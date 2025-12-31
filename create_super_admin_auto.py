import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_auto_admin():
    """
    Automated Super Admin Creator for Live Server
    Creates admin account without manual input for browser automation
    """
    User = get_user_model()
    
    # Credentials for client super admin
    username = 'client_admin'
    email = 'admin@nextgenerp.com'
    password = 'NextGen2025!Secure'
    
    print("=" * 50)
    print("🎓 NextGen ERP - Auto Super Admin Creator")
    print("=" * 50)
    
    try:
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User '{username}' already exists!")
            print("=" * 50)
            return
        
        # Create superuser
        user = User.objects.create_superuser(username, email, password)
        
        print(f"✅ SUCCESS! Super Admin Created")
        print("=" * 50)
        print("📝 CLIENT CREDENTIALS:")
        print(f"URL: https://yashamishra.pythonanywhere.com/admin/")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("=" * 50)
        print("🔒 IMPORTANT: Share these credentials securely!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("=" * 50)

if __name__ == "__main__":
    create_auto_admin()
