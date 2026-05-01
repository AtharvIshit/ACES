import os

base_path = r"d:\CodexPages\Finale\hiring\templates\base.html"

with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

# The script at the end currently looks like:
#     <footer>
#         ACES. &middot; Entry Level Hiring
#     </footer>
#     <style> ... </style>
#     {% block extra_head %}{% endblock %}
# </head>
# ...
# We need to find the stray <style> block that was added previously by accident
# and the stray {% block extra_head %}
# Note: My previous python script accidentally replaced the script tag with another style tag and closing head tag
# Let's fix it by completely replacing the end of the file.

# Find the footer to anchor our replace
footer_start = content.find('    <footer>\n        ACES. &middot; Entry Level Hiring\n    </footer>')

if footer_start != -1:
    content = content[:footer_start] + """    <footer>
        ACES. &middot; Entry Level Hiring
    </footer>
    {% block extra_js %}{% endblock %}
</body>
</html>"""

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed base.html")
