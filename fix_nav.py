import os
import shutil
from PIL import Image

SITE_DIR = r"c:\Users\Hrida\Downloads\dentist\downloaded_site\www.bombaydentalcompany.com"

# 1. Fix hero image: convert homepageimg.png -> homepageimg.jpg
png_path = os.path.join(SITE_DIR, "lovable-uploads", "homepageimg.png")
jpg_path = os.path.join(SITE_DIR, "lovable-uploads", "homepageimg.jpg")
if os.path.exists(png_path):
    Image.open(png_path).convert("RGB").save(jpg_path, "JPEG", quality=95)
    print(f"✅ Converted homepageimg.png -> homepageimg.jpg")
else:
    print(f"⚠️  homepageimg.png not found, skipping.")

# 2. Fix navigation: map route -> filename
# Files are named like "about_index.html" but links go to "/about"
route_map = {}
for fname in os.listdir(SITE_DIR):
    if fname.endswith("_index.html") and fname != "index.html":
        # e.g. "about_index.html" -> route "about"
        route = fname.replace("_index.html", "")
        route_map[route] = fname

print(f"\nFound {len(route_map)} routes to fix...")

for route, src_file in route_map.items():
    src = os.path.join(SITE_DIR, src_file)
    dest_dir = os.path.join(SITE_DIR, route)
    dest_file = os.path.join(dest_dir, "index.html")
    
    os.makedirs(dest_dir, exist_ok=True)
    if not os.path.exists(dest_file):
        shutil.copy2(src, dest_file)
        print(f"  ✅ /{route}/ -> {src_file}")
    else:
        print(f"  ⏭️  /{route}/ already exists, skipping.")

# Also handle nested routes like /services/invisalign
for fname in os.listdir(SITE_DIR):
    if fname.endswith("_index.html") and "/" not in fname:
        # handle services/invisalign style: "services_invisalign_index.html"
        parts = fname.replace("_index.html", "").split("_")
        if len(parts) >= 2:
            # could also just be a single-level like "about_index" already handled above
            pass

print("\n✅ All done! Restart your server and navigation should work.")
