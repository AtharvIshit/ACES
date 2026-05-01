import os

base_path = r"d:\CodexPages\Finale\hiring\templates\base.html"

with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace fonts
old_fonts = """    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=VT323&display=swap"
        rel="stylesheet">"""
new_fonts = """    <link
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Mono:wght@400;700&family=DotGothic16&display=swap"
        rel="stylesheet">"""
content = content.replace(old_fonts, new_fonts)

# Replace <style> block
start_style = content.find('<style>')
end_style = content.find('</style>') + len('</style>')

new_style = """<style>
        :root {
            /* "Nothing" Aesthetic Palette */
            --rosso: #FF0037;
            --rosso-hover: #D4002D;
            --rosso-soft: rgba(255, 0, 55, 0.15);
            --accent: #FF0037;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #FF0037;
            --border: #000000;
            --surface: #FFFFFF;
            --surface-alt: #F5F5F5;
            --bg: #F5F5F5;
            --text: #000000;
            --text-muted: #666666;

            --font-body: "Inter", sans-serif;
            --font-label: "Space Mono", monospace;
            --font-display: "DotGothic16", monospace;
        }

        [data-theme="dark"] {
            /* Retaining global Paper White standard, ignoring dark toggle per tech spec */
            --accent: #FF0037;
            --border: #000000;
            --surface: #FFFFFF;
            --surface-alt: #F5F5F5;
            --bg: #F5F5F5;
            --text: #000000;
            --text-muted: #666666;
            --rosso-soft: rgba(255, 0, 55, 0.15);
        }

        [data-theme="dark"] .bulb-icon {
            fill: var(--text);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-body) !important;
            background-color: var(--bg) !important;
            /* 16px Dot Grid Background */
            background-image: radial-gradient(#D1D1D1 1px, transparent 1px) !important;
            background-size: 16px 16px !important;
            color: var(--text) !important;
            min-height: 100vh;
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        form p,
        .form-group {
            margin-bottom: 24px !important;
            position: relative;
        }

        form label {
            display: block !important;
            font-family: 'Space Mono', monospace !important;
            font-size: 10px !important;
            color: #000000 !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            margin-bottom: 10px !important;
        }

        form input[type="text"],
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
        }

        form input:focus,
        form select:focus,
        .form-control:focus {
            border-color: #FF0037 !important;
            background-color: #FFFFFF !important;
            outline: none !important;
            box-shadow: none !important;
        }

        .dot-matrix {
            font-family: var(--font-display) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .label-font {
            font-family: var(--font-label) !important;
            font-size: 10px !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
        }

        .brutalist-border {
            border: 1px solid #000000 !important;
            border-radius: 0px !important;
        }

        .brutalist-corners {
            border-radius: 4px !important;
        }

        .glass-panel {
            background: #FFFFFF !important;
            border: 1px solid #000000 !important;
        }

        .navbar {
            padding: 0 2.5rem;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF !important;
            border-bottom: 1px solid #000000 !important;
            position: sticky;
            top: 0;
            z-index: 50;
        }

        .navbar a {
            color: #000000 !important;
            text-decoration: none;
            font-weight: 500;
            font-family: var(--font-label);
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .navbar a:hover {
            color: var(--rosso) !important;
        }

        .nav-links {
            display: flex;
            gap: 2rem;
            align-items: center;
        }

        .brand {
            font-family: var(--font-display);
            font-size: 28px;
            letter-spacing: 0.05em;
            color: #000000 !important;
            display: inline-flex;
            align-items: center;
            text-transform: uppercase;
        }

        .theme-toggle {
            display: none !important;
        }

        .container {
            max-width: 720px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }

        .container-wide {
            max-width: 900px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 99px !important;
            font-family: 'Space Mono', monospace !important;
            font-weight: bold;
            font-size: 12px !important;
            height: 48px;
            padding: 0 1.5rem;
            cursor: pointer;
            border: 1px solid #000000 !important;
            text-decoration: none;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 2px !important;
            background: #000000 !important;
            color: #FFFFFF !important;
            box-shadow: none !important;
        }

        .btn:hover {
            background: #FF0037 !important;
            border-color: #FF0037 !important;
            color: #FFFFFF !important;
        }
        
        .btn-secondary {
            background: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #000000 !important;
        }

        .btn-secondary:hover {
            background: #FF0037 !important;
            border-color: #FF0037 !important;
            color: #FFFFFF !important;
        }

        .card {
            background: #FFFFFF !important;
            border-radius: 0px !important;
            padding: 2rem;
            margin-bottom: 1.5rem;
            border: 1px solid #000000 !important;
            box-shadow: none !important;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-display) !important;
            font-weight: normal;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            color: #000000 !important;
            margin-bottom: 0.5rem;
        }

        .text-muted {
            color: #666666 !important;
            font-size: 0.9375rem;
            font-family: var(--font-body);
        }

        .messages {
            margin: 0 2rem 1.5rem;
        }

        .message {
            padding: 0.875rem 1.25rem;
            border-radius: 0px !important;
            margin-bottom: 0.5rem;
            font-size: 0.9375rem;
            font-family: var(--font-label);
            border: 1px solid #000000 !important;
        }

        .message.success {
            background: rgba(22, 163, 74, 0.1);
            color: var(--success);
            border-color: rgba(22, 163, 74, 1) !important;
        }

        .message.error {
            background: rgba(255, 0, 55, 0.1);
            color: var(--danger);
            border-color: rgba(255, 0, 55, 1) !important;
        }

        .form-check {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 0.75rem 0;
        }

        .form-check input {
            width: 18px;
            height: 18px;
            accent-color: var(--rosso) !important;
            background: #FFFFFF !important;
            border: 1px solid #000000 !important;
            border-radius: 0px !important;
        }

        ul.errorlist {
            color: var(--danger);
            font-size: 0.875rem;
            margin-top: 0.35rem;
            font-family: var(--font-label);
            list-style: none;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.625rem;
            border-radius: 0px !important;
            font-size: 0.8rem;
            font-family: var(--font-display) !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border: 1px solid #000000 !important;
        }

        .flex {
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
        }

        .mt-1 { margin-top: 0.5rem; }
        .mt-2 { margin-top: 1.5rem; }
        .mb-2 { margin-bottom: 1.5rem; }
        .mb-4 { margin-bottom: 3rem; }

        footer {
            text-align: center;
            padding: 3rem 2rem;
            color: #000000 !important;
            font-size: 10px;
            font-family: 'Space Mono', monospace !important;
            letter-spacing: 2px;
            border-top: 1px solid #000000 !important;
            text-transform: uppercase;
            background: #FFFFFF !important;
        }

        #system-log-ticker {
            background: #000000;
            color: #FFFFFF;
            font-family: 'Space Mono', monospace;
            font-size: 10px;
            letter-spacing: 2px;
            padding: 8px 16px;
            border-top: 1px solid #000000;
            text-transform: uppercase;
            display: flex;
            justify-content: space-between;
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            z-index: 100;
        }

        pre {
            font-family: 'Space Mono', monospace !important;
            white-space: pre-wrap;
            font-size: 0.9375rem;
            background: #F5F5F5 !important;
            border: 1px solid #000000 !important;
            padding: 1rem;
            border-radius: 0px !important;
            color: #000000 !important;
        }

        main a:not(.btn) {
            color: #000000 !important;
            text-decoration: none;
            border-bottom: 1px solid var(--rosso);
            transition: color 0.2s ease;
        }

        main a:not(.btn):hover {
            color: var(--rosso) !important;
        }
</style>"""

content = content[:start_style] + new_style + content[end_style:]

# Inject system log ticker before <footer>
system_log = """
    <div id="system-log-ticker">
        <span>> SYSTEM_STATUS: STABLE</span>
        <span>LATENCY: 14MS</span>
        <span>ENCRYPTION: AES-256</span>
    </div>
"""
if '<div id="system-log-ticker">' not in content:
    content = content.replace('    <footer>', system_log + '\n    <footer>')

# Remove the script block handling old theme toggles
begin_script = content.find('<script>')
end_script = content.find('</script>') + len('</script>')
if begin_script != -1 and end_script != -1:
    content = content[:begin_script] + content[end_script:]

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated base.html styling.")
