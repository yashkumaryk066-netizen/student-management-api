import os

VIEWS_FILE = '/home/tele/manufatures/student/views.py'
MODELS_FILE = '/home/tele/manufatures/student/models.py'

def move_imports_to_top(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    imports_to_move = []
    cleaned_lines = []
    
    # Heuristic: If we are in the "body" (after line 50 approx), any unindented import is suspicious/safe to move.
    # Actually, move ALL 'from student.models' and 'from .models' regardless of where they are, 
    # as long as they are unindented (which my sed command enforced).
    
    for i, line in enumerate(lines):
        # Check if line matches specific import patterns (unindented)
        if (line.startswith('from student.models') or 
            line.startswith('from .models') or
            line.startswith('import student.models')):
            
            imports_to_move.append(line.strip())
        else:
            cleaned_lines.append(line)

    # Unique imports
    imports_to_move = sorted(list(set(imports_to_move)))
    
    # Reconstruct file
    # Insert imports after the first few lines of imports (e.g. after line 10) or at start.
    # To be safe, insert at line 20 (after standard libs).
    
    final_lines = cleaned_lines[:20] + [imp + '\n' for imp in imports_to_move] + cleaned_lines[20:]
    
    with open(filepath, 'w') as f:
        f.writelines(final_lines)
    print(f"Fixed {filepath}: Moved {len(imports_to_move)} imports to top.")

move_imports_to_top(VIEWS_FILE)
# Models file might have similar issues if I stripped indentation there too.
move_imports_to_top(MODELS_FILE)
