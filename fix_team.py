import os

# We check both possible locations for the JS file
possible_paths = [
    r"c:\Users\Hrida\Downloads\dentist\assets\index-DjvQZ6bg.js",
    r"c:\Users\Hrida\Downloads\dentist\downloaded_site\www.bombaydentalcompany.com\assets\index-DjvQZ6bg.js"
]

target_js = None
for p in possible_paths:
    if os.path.exists(p):
        target_js = p
        break

if not target_js:
    print("❌ Error: Could not find the JavaScript file (index-DjvQZ6bg.js).")
    exit(1)

print(f"Reading {target_js}...")
with open(target_js, encoding='utf-8') as f:
    content = f.read()

# 1. Replace Siddhi Prabhu with Cosmetic Specialist
print("Updating Doctor 3...")
content = content.replace('Dr. Siddhi Prabhu (MDS)', 'Dr. Antima Saxena (MDS)')
content = content.replace('ENDODONTIST', 'COSMETIC DENTISTRY SPECIALIST')
old_bio1 = 'Our skilled Endodontist specializes in saving natural teeth through advanced root canal treatments, ensuring precision and pain-free care.'
new_bio1 = 'Expert in smile makeovers, dental veneers, and aesthetic enhancements with 13+ years of clinical excellence.'
content = content.replace(old_bio1, new_bio1)

# 2. Replace Jignesh Rajguru with Implant Specialist
print("Updating Doctor 4...")
content = content.replace('Dr. Jignesh Rajguru (MDS)', 'Dr. Antima Saxena (MDS)')
content = content.replace('ORAL SURGEON', 'IMPLANT & ORAL HEALTH SPECIALIST')
old_bio2 = 'Our expert Oral Surgeon performs complex dental surgeries with utmost precision, offering safe and comfortable solutions for all your oral health needs.'
new_bio2 = 'Specializing in advanced dental implants and comprehensive oral rehabilitation to restore your confident smile with 13+ years experience.'
content = content.replace(old_bio2, new_bio2)

# Save the file
with open(target_js, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated team section!")
print("Now run 'git add .', 'git commit', and 'git push' to update your live site.")
