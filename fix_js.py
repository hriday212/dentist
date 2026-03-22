"""
Fix broken JavaScript syntax caused by apostrophes in text replacements.
The replacement of 'Bombay Dental' with 'Dr. Saxena\'s...' broke single-quoted JS strings.
This script fixes those by using unicode right apostrophe (u2019) in the JS file.
"""
import re

JS_FILE = r"c:\Users\Hrida\Downloads\dentist\downloaded_site\www.bombaydentalcompany.com\assets\index-DjvQZ6bg.js"

print("Reading JS file...")
with open(JS_FILE, encoding='utf-8') as f:
    content = f.read()

original_len = len(content)

# Fix all variants of the broken apostrophe replacements
# Replace straight apostrophe version with curly/unicode apostrophe
fixes = [
    ("Dr. Saxena's", "Dr. Saxena\u2019s"),
    ("dr. saxena's", "dr. saxena\u2019s"),
    ("DR. SAXENA'S", "DR. SAXENA\u2019S"),
    ("Saxena's", "Saxena\u2019s"),
    ("saxena's", "saxena\u2019s"),
]

total_fixed = 0
for old, new in fixes:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed {count}x: '{old}' -> '{new}'")
        total_fixed += count

# Verify no more broken patterns
remaining = content.count("'saxena'") + content.count("'Saxena'")
print(f"\n✅ Fixed {total_fixed} broken strings")
print(f"Remaining suspicious patterns: {remaining}")

with open(JS_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ JS file saved. Do Ctrl+Shift+R to test the dropdown.")
