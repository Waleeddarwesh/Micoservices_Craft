import json
import os
import ast

log_path = r'C:\Users\walid\.gemini\antigravity-ide\brain\16b69ed6-b61a-41b6-a5ac-e1372041742e\.system_generated\logs\transcript.jsonl'
files_to_restore = {}
with open(log_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if 'tool_calls' in data:
                for tc in data['tool_calls']:
                    if tc['name'] == 'write_to_file':
                        target = tc['args'].get('TargetFile', '')
                        if 'sysadmin_dashboard\\\\js\\\\pages' in target or 'sysadmin_dashboard/js/pages' in target:
                            # The file content is in CodeContent, might have escaped quotes
                            files_to_restore[target] = tc['args']['CodeContent']
        except Exception as e: pass

for t, content in files_to_restore.items():
    t_clean = ast.literal_eval(t) if t.startswith('"') else t
    c_clean = ast.literal_eval(content) if content.startswith('"') else content
    
    # Clean the path
    t_clean = t_clean.replace('\\\\', '\\')
    
    # Now fix the backslash escape bug!
    c_clean = c_clean.replace('\\`', '`').replace('\\$', '$')
    with open(t_clean, 'w', encoding='utf-8') as out:
        out.write(c_clean)

print(f'Restored {len(files_to_restore)} files!')
