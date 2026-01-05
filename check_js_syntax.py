
def check_syntax(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    stack = []
    
    # Ignore strings/comments logic is hard to implement perfectly in regex, 
    # but let's try a basic stack check.
    
    for i, line in enumerate(lines):
        line_num = i + 1
        # Remove strings (simple quote removal)
        clean_line = ""
        in_string = False
        quote_char = None
        for char in line:
            if char in ["'", '"', '`']:
                if not in_string:
                    in_string = True
                    quote_char = char
                elif char == quote_char:
                    in_string = False
                    quote_char = None
                continue
            if not in_string:
                clean_line += char
        
        # Remove comments //
        if '//' in clean_line:
            clean_line = clean_line.split('//')[0]
            
        for char in clean_line:
            if char in ['(', '{', '[']:
                stack.append((char, line_num))
            elif char in [')', '}', ']']:
                if not stack:
                    print(f"Error: Unmatched '{char}' at line {line_num}")
                    return
                last, last_line = stack.pop()
                if (last == '(' and char != ')') or \
                   (last == '{' and char != '}') or \
                   (last == '[' and char != ']'):
                    print(f"Error: Mismatched '{last}' (line {last_line}) closed by '{char}' at line {line_num}")
                    return

    if stack:
        print(f"Error: Unclosed '{stack[-1][0]}' from line {stack[-1][1]}")
    else:
        print("No mismatched brackets found.")

if __name__ == "__main__":
    check_syntax("static/js/dashboard/admin.js")
