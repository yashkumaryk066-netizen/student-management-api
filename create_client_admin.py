import os
import django
import sys

# Setup Django environment
sys.path.append('/home/yashamishra/student-management-api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_client_admin():
    print("🚀 Client Admin Creator Tool")
    print("----------------------------")
    
    username = input("Enter Client Username (e.g., school_admin): ")
    email = input("Enter Client Email: ")
    password = input("Enter Secure Password: ")
    
    User = get_user_model()
    
    if User.objects.filter(username=username).exists():
        print(f"❌ Error: User '{username}' already exists!")
        return

    try:
        # Create superuser (Admin level access)
        user = User.objects.create_superuser(username, email, password)
        print(f"\n✅ Success! User '{username}' created.")
        print("----------------------------")
        print("📝 SEND THESE DETAILS TO CLIENT:")
        print(f"URL: https://yashamishra.pythonanywhere.com/admin/")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("----------------------------")
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")

if __name__ == "__main__":
    create_client_admin()
