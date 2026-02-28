import os
import re

BASE_DIR = '/home/tele/manufatures'

# Map deleted module -> new module
# (Assuming all these were successfully merged)
MODULE_MAP = {
    # Models
    'student.chat_models': 'student.models',
    'student.models.chat_models': 'student.models',
    
    # Views
    'student.ai_auth_views': 'student.views',
    'student.ai_chat_views': 'student.views',
    'student.ai_logout_view': 'student.views',
    'student.approval_views': 'student.views',
    'student.attendance_geo_views': 'student.views',
    'student.chat_api': 'student.views',
    'student.chatgpt_views': 'student.views',
    'student.eazypay_views': 'student.views',
    'student.manual_payment_views': 'student.views',
    'student.onboarding_views': 'student.views',
    'student.password_reset_views': 'student.views',
    'student.payment_gateway_views': 'student.views',
    'student.plan_features_views': 'student.views',
    'student.report_views': 'student.views',
    'student.student_portal_views': 'student.views',
    'student.subscription_views': 'student.views',
    'student.super_admin_views': 'student.views',
    'student.team_views': 'student.views',
    'student.unified_ai_views': 'student.views',
    'student.admin_dashboard_views': 'student.views',
}

# Regex to match 'from X import Y'
# We want to replace X with MODULE_MAP[X] if it exists.

def process_file(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    modified = False
    
    for line in lines:
        # Check for 'from student.xxx import'
        match = re.match(r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import', line)
        if match:
            module_name = match.group(1)
            if module_name in MODULE_MAP:
                new_module = MODULE_MAP[module_name]
                # Replace the module name
                new_line = line.replace(f'from {module_name}', f'from {new_module}')
                new_lines.append(new_line)
                modified = True
                continue
                
        new_lines.append(line)
        
    if modified:
        with open(filepath, 'w') as f:
            f.writelines(new_lines)
        print(f"Fixed imports in: {filepath}")

# Walk through project
for root, dirs, files in os.walk(BASE_DIR):
    if '_backup' in root or '__pycache__' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            process_file(os.path.join(root, file))
