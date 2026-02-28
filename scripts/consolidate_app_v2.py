import os

# Paths
BASE_DIR = '/home/tele/manufatures/student'
# We access backups now
MODELS_DIR = os.path.join(BASE_DIR, 'models_backup')
VIEWS_DIR = os.path.join(BASE_DIR, 'views_backup')
OUTPUT_MODELS = os.path.join(BASE_DIR, 'models.py')
OUTPUT_VIEWS = os.path.join(BASE_DIR, 'views.py')

# File Orders
model_files = [
    'base.py', 'users.py', 'academic.py', 'attendance.py', 'finance.py', 
    'hostel.py', 'transport.py', 'library.py', 'hr.py', 'exam.py', 
    'event.py', 'communication.py', 'coaching.py', 'ai.py', 'chat_models.py'
]

view_files = [
    'base.py', 'users.py', 'academic.py', 'finance.py', 'attendance.py', 
    'hostel.py', 'transport.py', 'library.py', 'hr.py', 'exam.py', 
    'event.py', 'coaching.py', 'communication.py', 'search.py', 
    'calendar.py', 'bulk.py', 'report.py', 'seo.py', 'pwa.py', 'dashboard.py',
    'super_admin_api.py', 'team_views.py'
]

def is_internal_import(line, type_):
    # Check if the line is importing a module that is being merged
    line = line.strip()
    if not line.startswith('from .'):
        return False
        
    # Extract module name "from .module import"
    parts = line.split()
    if len(parts) < 2: return False
    module_field = parts[1] # ".module" or ".module.sub"
    module_name = module_field.lstrip('.')
    
    if type_ == "Models":
        # In models.py, we merge everything in model_files
        # Note: model_files has extensions .py, module name is without .py
        merged_modules = [m.replace('.py', '') for m in model_files]
        if module_name in merged_modules: return True
        return False
        
    if type_ == "Views":
        merged_modules = [m.replace('.py', '') for m in view_files]
        if module_name in merged_modules: return True
        # Also skip 'admin_dashboard_views' imports if we are handling it later?
        # But 'from .admin_dashboard_views' is from ROOT. relative import might look different.
        # Assuming view_files only covers the 'student/views/' directory usage.
        return False
    
    return False

def consolidate(directory, file_list, output_file, type_):
    all_lines = []
    
    # Pre-add standard imports if needed? 
    # No, rely on file content.
    
    for filename in file_list:
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue
            
        all_lines.append(f"\n# --- FROM {filename} ---\n")
        
        with open(path, 'r') as f:
            lines = f.readlines()
            
        skipping = False
        
        for line in lines:
            stripped = line.strip()
            
            # State machine for skipping multiline imports of internal modules
            if skipping:
                if ')' in line:
                    skipping = False
                continue
            
            if is_internal_import(line, type_):
                if '(' in line and ')' not in line:
                    skipping = True
                continue
                
            all_lines.append(line)

    with open(output_file, 'w') as f:
        f.writelines(all_lines)

    print(f"Created {output_file}")

# Execution
consolidate(MODELS_DIR, model_files, OUTPUT_MODELS, "Models")
consolidate(VIEWS_DIR, view_files, OUTPUT_VIEWS, "Views")
