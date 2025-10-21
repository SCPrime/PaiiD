#!/bin/bash
# 🔒 LOCKED FINAL File Guardian
# This script intercepts file read operations in Cursor and forces AI to ask permission
# before accessing protected files.

read payload
file_path=$(echo "$payload" | jq -r .file_path)

# Check if file is in LOCKED FINAL folder or matches protected patterns
if [[ "$file_path" =~ "LOCKED FINAL" ]] || \
   [[ "$file_path" =~ "CompletePaiiDLogo" ]] || \
   [[ "$file_path" =~ "PaiiDChatBoxLocked" ]] || \
   [[ "$file_path" =~ "iPi-Symbol-Locked" ]]; then

  # Force AI to ask permission with scary warning
  jq -n \
    --arg msg "🔒 **LOCKED FINAL FILE DETECTED**

⚠️ **WARNING:** You are attempting to read a PROTECTED REFERENCE FILE:
📁 File: $file_path

🚫 **RULES - NO EXCEPTIONS:**
1. These files are READ-ONLY REFERENCES
2. DO NOT MODIFY, REFACTOR, or \"IMPROVE\"
3. COPY ONLY - Never edit the original
4. NO REFORMATTING - Keep exact spacing/styling

❓ **Do you have explicit permission from the user to access this file?**

✅ If YES: The user explicitly asked you to read this for reference
❌ If NO: Ask the user first before proceeding

**Status:** IMMUTABLE | **Approved By:** Dr. SC Prime ✅" \
    '{continue: true, permission: "ask", userMessage: $msg}'
else
  # Allow access to all other files
  jq -n '{continue: true, permission: "allow"}'
fi
