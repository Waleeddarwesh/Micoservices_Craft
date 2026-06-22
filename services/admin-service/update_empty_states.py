import os
import re

directory = 'sysadmin_dashboard/js/pages'

empty_state_template = """<tr><td colspan="{colspan}" style="text-align:center;padding:var(--space-10);color:var(--clr-text-muted)">
    <div class="empty-state" style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:32px 0;">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" style="color:{icon_color};margin-bottom:16px;">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="15" x2="15" y2="15"/>
        </svg>
        <h3 style="margin-bottom:8px;color:var(--clr-text);font-size:var(--fs-md);font-weight:var(--fw-semibold);">{title}</h3>
        <p style="color:var(--clr-text-muted);font-size:var(--fs-sm);">{message}</p>
    </div>
</td></tr>"""

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.js'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            def replacer(match):
                colspan = match.group(1)
                classes = match.group(2)
                message = match.group(3)
                
                if 'Loading' in message or 'loading' in message.lower():
                    return f'<tr><td colspan="{colspan}" class="{classes}"><div style="display:flex;flex-direction:column;align-items:center;padding:32px 0;"><div class="spinner" style="margin-bottom:16px;"></div><p style="color:var(--clr-text-muted)">{message}</p></div></td></tr>'
                
                title = "${window.t('No Data Available')}"
                icon_color = "var(--clr-border)"
                
                if 'text-danger' in classes or 'Failed' in message:
                    title = "${window.t('Error')}"
                    icon_color = "var(--clr-danger)"
                
                # If there's backticks inside the message, escape them or don't worry because the outer string is backticks?
                # Actually, the original message is already inside backticks. e.g. `${window.t('No backup jobs found.')}`
                # We can just inject it.
                return empty_state_template.replace('{colspan}', colspan).replace('{message}', message).replace('{title}', title).replace('{icon_color}', icon_color)

            new_content = re.sub(r'<tr>\s*<td\s+colspan="(\d+)"\s+class="([^"]+)">\s*(.*?)\s*</td>\s*</tr>', replacer, content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
