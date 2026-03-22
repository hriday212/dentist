import os
import requests

DEST_DIR = r"c:\Users\Hrida\Downloads\dentist\downloaded_site\www.bombaydentalcompany.com\lovable-uploads"
BASE_URL = "https://www.bombaydentalcompany.com/lovable-uploads/"

# List all files in the folder and try to restore each one from the live site
restored = 0
failed = 0

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}

for fname in os.listdir(DEST_DIR):
    if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        continue
    url = BASE_URL + fname
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200 and len(r.content) > 5000:  # real image, not tiny error
            with open(os.path.join(DEST_DIR, fname), 'wb') as f:
                f.write(r.content)
            print(f"  ✅ Restored: {fname} ({len(r.content)//1024}KB)")
            restored += 1
        else:
            print(f"  ⚠️  Skipped: {fname} (status {r.status_code}, {len(r.content)} bytes)")
            failed += 1
    except Exception as e:
        print(f"  ❌ Error: {fname}: {e}")
        failed += 1

print(f"\nDone! Restored {restored}, could not restore {failed}.")
