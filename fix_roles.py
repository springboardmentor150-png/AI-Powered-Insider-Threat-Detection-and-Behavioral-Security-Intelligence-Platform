import os
import re

directories = ['backend/app/routes', 'backend/app']
files_to_fix = [
    'backend/app/routes/employee_routes.py',
    'backend/app/routes/incident_routes.py',
    'backend/app/routes/analytics_routes.py',
    'backend/app/main.py'
]

for filepath in files_to_fix:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace "manager" with "security_manager" inside require_role.
        content = re.sub(r'"manager"', '"security_manager"', content)
        content = re.sub(r'"MANAGER"', '"SECURITY_MANAGER"', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Roles fixed.")
