import os
import shutil

BASE_DIR = '/home/tele/manufatures/student'
BACKUP_DIR = os.path.join(BASE_DIR, 'root_backup')
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

files_to_move = [
    'ai_auth_views.py', 'ai_chat_views.py', 'ai_logout_view.py',
    'approval_views.py', 'attendance_geo_views.py', 'chat_api.py',
    'chatgpt_views.py', 'eazypay_views.py', 'manual_payment_views.py',
    'onboarding_views.py', 'password_reset_views.py', 'payment_gateway_views.py',
    'plan_features_views.py', 'report_views.py', 'student_portal_views.py',
    'subscription_views.py', 'super_admin_views.py', 'team_views.py',
    'unified_ai_views.py', 'admin_dashboard_views.py', 'chat_models.py'
]

for filename in files_to_move:
    src = os.path.join(BASE_DIR, filename)
    dst = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"Moved {filename}")
    else:
        print(f"Not found: {filename}")
