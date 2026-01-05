
def check_balance(filename):
    with open(filename, 'r') as f:
        text = f.read()

    stack = []
    lines = text.split('\n')
    
    # State
    in_string = False
    quote_char = None
    in_template = False
    in_comment_line = False
    in_comment_block = False
    
    # Map raw index to line number
    def get_line_num(idx):
        return text[:idx].count('\n') + 1

    for i, char in enumerate(text):
        # Update line context (not strictly needed for char-by-char, but good for skipping // comments)
        
        # Strings/Comments Logic
        if in_comment_line:
            if char == '\n':
                in_comment_line = False
            continue
            
        if in_comment_block:
            if char == '/' and i > 0 and text[i-1] == '*':
                in_comment_block = False
            continue

        if in_string:
            if char == quote_char and (i == 0 or text[i-1] != '\\'): # Ignore escaped
                in_string = False
            continue
            
        if in_template:
            if char == '`' and (i == 0 or text[i-1] != '\\'):
                in_template = False
            elif char == '{' and i > 0 and text[i-1] == '$':
                 # This is ${ inside template, acts like block start? 
                 # Actually JS parsers treat ${ as start of expression.
                 # Effectively we can treat { as normal block opener
                 stack.append(('{', get_line_num(i)))
            elif char == '}':
                 # Check if this } closes a ${
                 if stack and stack[-1][0] == '{':
                      # We assume it closes the ${...}, so it's fine.
                      # Ideally we'd track if the top of stack was pushed by ${
                      pass
            # Just verify braces balance inside template
            pass
            # Note: template literal logic is complex. 
            # Simple approach: If in template, ONLY process ${} as braces?
            # Or assume template content doesn't contain unmatched braces?
            
        # Helper to start states
        if char == '/' and i+1 < len(text):
            if text[i+1] == '/':
                in_comment_line = True
                continue
            elif text[i+1] == '*':
                in_comment_block = True
                continue
        
        if char in ["'", '"']:
            in_string = True
            quote_char = char
            continue
            
        if char == '`':
            in_template = not in_template
            continue

        # Brackets
        if char in ['(', '{', '[']:
            stack.append((char, get_line_num(i)))
        elif char in [')', '}', ']']:
            if not stack:
                print(f"ERROR: Unmatched '{char}' at line {get_line_num(i)}")
                # Continue finding more? No, usually fatal.
                return
            last, last_line = stack.pop()
            
            # Check match
            expected = {'(':')', '{':'}', '[':']'}[last]
            if char != expected:
                print(f"ERROR: Mismatched '{last}' (line {last_line}) closed by '{char}' at line {get_line_num(i)}")
                return

    if stack:
        print(f"ERROR: Unclosed '{stack[-1][0]}' from line {stack[-1][1]}")
    else:
        print("Balance OK.")

if __name__ == "__main__":
    check_balance("static/js/dashboard/admin.js")
