import os

# Login
login_path = r"d:\CodexPages\Finale\hiring\templates\hiring\login.html"
with open(login_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<div style="max-width: 400px; margin: 4rem auto;">', '<div class="card brutalist-corners brutalist-border" style="max-width: 400px; margin: 4rem auto; padding: 3rem; background: #FFFFFF; border-radius: 0px !important;">')
content = content.replace('class="btn btn-primary"', 'class="btn btn-primary" style="width: 100%; height: 52px; font-size: 16px; letter-spacing: 0.1em; text-transform: uppercase;"')

with open(login_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Signup
signup_path = r"d:\CodexPages\Finale\hiring\templates\hiring\signup.html"
with open(signup_path, 'r', encoding='utf-8') as f:
    s_content = f.read()

s_content = s_content.replace('background: var(--bg);', 'background: #FFFFFF;')
s_content = s_content.replace('border: 1px solid var(--border);', 'border: 1px solid #000000;')
s_content = s_content.replace('color: var(--text-muted);', 'color: #000000;')
s_content = s_content.replace('color: #666666;', 'color: #000000;')
s_content = s_content.replace('color: #FFFFFF;', 'color: #000000;')
s_content = s_content.replace('background: var(--surface);', 'background: #FFFFFF;')
s_content = s_content.replace('color: #666;', 'color: #000000;')
s_content = s_content.replace('btn btn-primary', 'btn')

with open(signup_path, 'w', encoding='utf-8') as f:
    f.write(s_content)

print("Updated Auth views")
