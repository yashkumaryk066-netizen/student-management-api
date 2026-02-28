import re

URLS_FILE = '/home/tele/manufatures/student/urls.py'

# Logic:
# 1. Read file.
# 2. Iterate lines.
# 3. If line matches pattern 'from .[*] import', replace with 'from .views import'.
# 4. If line matches 'from .views.[*] import', replace with 'from .views import'.
# 5. Handle multi-line imports (parentheses).

# Modules that were merged into views.py:
MERGED_VIEW_MODULES = [
    'academic', 'finance', 'attendance', 'users', 'hostel', 'transport', 'library', 'hr',
    'exam', 'event', 'coaching', 'communication', 'dashboard', 'search', 'calendar', 'bulk',
    'report', 'seo', 'pwa', 'super_admin_api', 'team_views', 'admin_dashboard_views',
    # Appended root views
    'ai_auth_views', 'ai_chat_views', 'ai_logout_view', 'approval_views', 'attendance_geo_views',
    'chat_api', 'chatgpt_views', 'eazypay_views', 'manual_payment_views', 'onboarding_views',
    'password_reset_views', 'payment_gateway_views', 'plan_features_views', 'report_views',
    'student_portal_views', 'subscription_views', 'super_admin_views', 'unified_ai_views',
    'admin_dashboard_views'
]

# Regex for 'from .module import ...'
# We capture the module name to check if it's in our list.
import_pattern = re.compile(r'^from \.([a-zA-Z0-9_]+) import')
# Regex for 'from .views.module import ...'
nested_import_pattern = re.compile(r'^from \.views\.([a-zA-Z0-9_]+) import')

with open(URLS_FILE, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    # Check for direct relative import
    match = import_pattern.match(line)
    if match:
        module_name = match.group(1)
        if module_name in MERGED_VIEW_MODULES or module_name == 'views': 
            # If it's already 'views', keep it (or merge logic handles it)
            # If match, replace 'from .module' with 'from .views'
            new_lines.append(line.replace(f'from .{module_name}', 'from .views'))
        else:
            new_lines.append(line)
        continue

    # Check for nested views import
    match_nested = nested_import_pattern.match(line)
    if match_nested:
         module_name = match_nested.group(1)
         # Assume all under .views are merged
         new_lines.append(line.replace(f'from .views.{module_name}', 'from .views'))
         continue

    new_lines.append(line)

# Clean up duplicate imports if any?
# Python handles 'from .views import A' and 'from .views import B' fine.
# But we might have 'from .views import' multiple times. It's valid python.

with open(URLS_FILE, 'w') as f:
    f.writelines(new_lines)

print("Fixed urls.py imports.")
