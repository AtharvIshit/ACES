import os

# Update signup.html
signup_path = r"d:\CodexPages\Finale\hiring\templates\hiring\signup.html"
with open(signup_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("family=DotGothic16", "family=Space+Grotesk:wght@400;700&family=JetBrains+Mono:wght@400;700")
content = content.replace("'DotGothic16'", "'Space Grotesk'")
content = content.replace("'Space Grotesk'", "'JetBrains Mono'") # The form labels were previously using Space Grotesk here, switching to JetBrains Mono per instruction

with open(signup_path, 'w', encoding='utf-8') as f:
    f.write(content)


# Update attempt_take.html JS Charts
attempt_list = r"d:\CodexPages\Finale\hiring\templates\hiring\attempt_list.html"
with open(attempt_list, 'r', encoding='utf-8') as f:
    al_content = f.read()

al_content = al_content.replace("'\"DotGothic16\", monospace'", "'\"JetBrains Mono\", monospace'")
al_content = al_content.replace("'\"Space Mono\", monospace'", "'\"JetBrains Mono\", monospace'")

with open(attempt_list, 'w', encoding='utf-8') as f:
    f.write(al_content)

print("Updated sub-templates")
