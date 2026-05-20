---
description: Create a single dummy user in the database
allowed-tools: Read, Bash(python3:*), Bash(bash:*)
---

Read database/db.py to understand the users table
schema and the get_db() helper.

Run the logic directly using Bash with an inline Python heredoc
(do NOT create or save any .py file). Use this pattern:

```bash
python3 - <<'EOF'
# your inline python code here
EOF
```

The inline script must:
1. Generate a realistic random Indian user:
   - Name: a realistic Indian first + last name
   - Email: derived from the name with a random 2-3 digit
     number suffix (e.g. rahul.sharma91@gmail.com)
   - Password: "password123" hashed with werkzeug's
     generate_password_hash
   - created_at: current datetime

2. Check if the generated email already exists in the
   users table. If it does, regenerate until unique.

3. Insert the user using the same get_db() pattern from db.py.

4. Print confirmation:
   - id
   - name
   - email