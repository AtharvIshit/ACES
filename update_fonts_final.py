import os

# Update base.html to enforce 60px input heights and box-sizing globally
base_path = r"d:\CodexPages\Finale\hiring\templates\base.html"
with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure inputs are exactly 60px and border-box
old_input_css = """        form input[type="text"],
        form input[type="email"],
        form input[type="password"],
        form select,
        .form-control {
            width: 100% !important;
            height: 60px !important;
            background-color: #FFFFFF !important;
            border: 1px solid #000000 !important;
            border-radius: 0px !important;
            color: #000000 !important;
            padding: 0 18px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 16px !important;
            transition: all 0.2s ease-in-out !important;
            box-sizing: border-box !important;
            box-shadow: none !important;
        }"""
        
# It already seems to have box-sizing and 60px height. Let's ensure JetBrains Mono is in the badge/button elements where needed.
content = content.replace("font-family: 'Space Mono', monospace", "font-family: 'JetBrains Mono', monospace")

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Fix remaining attempt_take.html
attempt_take = r"d:\CodexPages\Finale\hiring\templates\hiring\attempt_take.html"
with open(attempt_take, 'r', encoding='utf-8') as f:
    at_content = f.read()

at_content = at_content.replace("'Space Mono', monospace", "'JetBrains Mono', monospace")

with open(attempt_take, 'w', encoding='utf-8') as f:
    f.write(at_content)

print("Swept typography globally")
