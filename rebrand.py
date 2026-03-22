import os
from pathlib import Path
from bs4 import BeautifulSoup
import re

TARGET_DIR = r"c:\Users\Hrida\Downloads\dentist\downloaded_site\www.bombaydentalcompany.com"

# The new map embed URL
NEW_MAP_SRC = "https://maps.google.com/maps?q=Dr.+Saxena's+Dental+%26+Medical+Center,+Nerul,+Navi+Mumbai&hl=en&z=15&output=embed"

REPLACEMENTS = {
    # Names
    "Bombay Dental Company": "Dr. Saxena's Dental & Cosmetic Studio",
    "Bombay Dental": "Dr. Saxena's Dental",
    "Bombay%20Dental": "Dr.%20Saxena's%20Dental",
    "bombaydentalcompany.com": "dr-saxena-dental.vercel.app",
    
    # Doctors
    "Dr. Tushita Singh": "Dr. Saxena",
    "Dr. Tushita": "Dr. Saxena",
    "Dr. Shreya Batra": "Dr. Saxena", # User mentioned this in earlier request
    
    # Location Specific
    "Best dentist in Worli": "Best dentist in Nerul, Navi Mumbai",
    "dentist in Worli": "dentist in Nerul",
    "Worli, Mumbai": "Nerul, Mumbai",
    "Worli": "Nerul",
    
    # Address
    "Atur House, 1st floor, flat no. 2, Worli Naka, Worli, Mumbai - 400018": "Shop No 1, Dr. Saxena's Dental & Medical Center, Jain Park co-op society, sector 20, Nerul West, Nerul, Navi Mumbai, Maharashtra 400706",
    
    # Phone number formats
    "88826 72980": "7045467444",
    "8882672980": "7045467444",
    "8882 672 980": "7045 467 444",
    "022 2490 1234": "07045467444",
    
    # Email
    "bombaydentalcompany@gmail.com": "No Email Available (Call Us)",
    "info@bombaydental.com": "Contact via Phone (07045467444)",
}

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
        
    # Standard text replacements
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)
        content = content.replace(old.upper(), new.upper())
        content = content.replace(old.lower(), new.lower())
    
    # Catch any remaining standalone "Bombay" (case-insensitive)
    content = re.sub(r'Bombay', "Dr. Saxena's", content, flags=re.IGNORECASE)
    
    # Fix mailto links specifically
    content = re.sub(r'mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', r'tel:+917045467444', content)
    
    # Replace Maps Iframe
    soup = BeautifulSoup(content, 'html.parser')
    iframes = soup.find_all('iframe')
    modified_iframe = False
    for iframe in iframes:
        if 'google.com/maps' in iframe.get('src', ''):
            iframe['src'] = NEW_MAP_SRC
            modified_iframe = True
            
    if modified_iframe:
        content = str(soup)

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main(target_dir):
    print(f"Starting rebranding process in {target_dir}...")
    
    html_modified = 0
    js_modified = 0
    
    for root, _, files in os.walk(target_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith('.html'):
                if process_file(filepath):
                    html_modified += 1
            elif file.endswith('.js'):
                if process_file(filepath):
                    js_modified += 1
                    
    print(f"\nRebranding complete!")
    print(f"Modified {html_modified} HTML files.")
    print(f"Modified {js_modified} JS files.")

if __name__ == "__main__":
    main(TARGET_DIR)
