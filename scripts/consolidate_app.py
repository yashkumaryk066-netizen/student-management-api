import os
import re

# Paths
BASE_DIR = '/home/tele/manufatures/student'
MODELS_DIR = os.path.join(BASE_DIR, 'models')
VIEWS_DIR = os.path.join(BASE_DIR, 'views')
OUTPUT_MODELS = os.path.join(BASE_DIR, 'models.py')
OUTPUT_VIEWS = os.path.join(BASE_DIR, 'views.py')

# File Orders
model_files = [
    'base.py', 'users.py', 'academic.py', 'attendance.py', 'finance.py', 
    'hostel.py', 'transport.py', 'library.py', 'hr.py', 'exam.py', 
    'event.py', 'communication.py', 'coaching.py', 'ai.py'
]

view_files = [
    'base.py', 'users.py', 'academic.py', 'finance.py', 'attendance.py', 
    'hostel.py', 'transport.py', 'library.py', 'hr.py', 'exam.py', 
    'event.py', 'coaching.py', 'communication.py', 'search.py', 
    'calendar.py', 'bulk.py', 'report.py', 'seo.py', 'pwa.py', 'dashboard.py',
    'super_admin_api.py', 'team_views.py'
]

def consolidate(directory, file_list, output_file, type_):
    all_content = ""
    imports = set()
    code_blocks = []

    for filename in file_list:
        path = os.path.join(directory, filename)
        if not os.path.exists(path):
            print(f"Skipping missing file: {path}")
            continue
            
        with open(path, 'r') as f:
            lines = f.readlines()
            
        file_code = []
        for line in lines:
            line_stripped = line.strip()
            # Collect imports to move to top
            if (line_stripped.startswith('import ') or line_stripped.startswith('from ')) and not 'student.models' in line and not 'student.views' in line and not line_stripped.startswith('from .'):
                imports.add(line)
            # Skip relative imports within the module we are merging
            elif line_stripped.startswith('from .'):
                pass 
            else:
                file_code.append(line)
        
        button_comment = f"\n# --- FROM {filename} ---\n"
        code_blocks.append(button_comment + "".join(file_code))

    with open(output_file, 'w') as f:
        f.write("# Consolidated " + type_ + " File\n")
        # Write imports
        f.write("".join(sorted(list(imports))))
        f.write("\n\n")
        # Write code
        f.write("".join(code_blocks))

    print(f"Created {output_file}")

# Execution
consolidate(MODELS_DIR, model_files, OUTPUT_MODELS, "Models")
consolidate(VIEWS_DIR, view_files, OUTPUT_VIEWS, "Views")
