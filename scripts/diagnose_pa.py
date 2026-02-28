
import os
import sys
import django
from django.conf import settings

# 1. Add project to path (simulate WSGI)
sys.path.append(os.getcwd())

# 2. Set settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'manufatures.settings')

print("Step 1: Environment Setup... OK")

# 3. Import WSGI handler (this triggers app loading)
try:
    print("Step 2: Attempting to import WSGI application...")
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("✅ SUCCESS: WSGI Application loaded successfully!")
    print("The 500 error is NOT caused by code syntax or import errors.")
except Exception as e:
    print("\n❌ CRITICAL ERROR: The application failed to start.")
    print("-" * 60)
    import traceback
    traceback.print_exc()
    print("-" * 60)
    print("Please fix the error above to resolve the 500 error.")
