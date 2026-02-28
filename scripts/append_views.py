import os

BASE_DIR = '/home/tele/manufatures/student'
OUTPUT_VIEWS = os.path.join(BASE_DIR, 'views.py')

additional_views = [
    'ai_auth_views.py', 'ai_chat_views.py', 'ai_logout_view.py',
    'approval_views.py', 'attendance_geo_views.py', 'chat_api.py',
    'chatgpt_views.py', 'eazypay_views.py', 'manual_payment_views.py',
    'onboarding_views.py', 'password_reset_views.py', 'payment_gateway_views.py',
    'plan_features_views.py', 'report_views.py', 'student_portal_views.py',
    'subscription_views.py', 'super_admin_views.py', 'team_views.py',
    'unified_ai_views.py'
]

with open(OUTPUT_VIEWS, 'a') as outfile:
    for filename in additional_views:
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            print(f"Appending {filename}...")
            outfile.write(f"\n\n# --- FROM ROOT/{filename} ---\n")
            with open(path, 'r') as infile:
                for line in infile:
                    # Filter imports that break things? 
                    # If I import 'from .models import X', and models is now a file, it works.
                    # If I import 'from .views import Y', it might be circular if not careful, but usually ok inside functions.
                    # Standard imports should be fine.
                    outfile.write(line)
        else:
            print(f"File {filename} not found.")

print("Appended all views.")
