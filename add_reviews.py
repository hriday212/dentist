from bs4 import BeautifulSoup
import os

filepath = r"c:\Users\Hrida\Downloads\dentist\downloaded_site\www.bombaydentalcompany.com\index.html"

with open(filepath, 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

# Find the paragraph containing "1200+ 5 star reviews!"
for p in soup.find_all('p'):
    if '1200+' in p.text and 'reviews' in p.text:
        # Create a new bold Google badge element
        new_html = BeautifulSoup('''
        <div class="flex flex-col items-center justify-center mt-2">
            <div class="flex items-center gap-2 mb-2">
                <span class="text-2xl font-bold text-gray-800">5.0</span>
                <div class="flex text-yellow-500">
                    <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                    <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                    <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                    <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                    <svg class="w-6 h-6 fill-current" viewBox="0 0 24 24"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>
                </div>
            </div>
            <p class="text-lg md:text-xl text-gray-800 font-semibold">Rated 5 Stars on Google Maps!</p>
        </div>
        ''', 'html.parser')
        p.replace_with(new_html)
        break

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(str(soup))
print("Added Google Testimonials to index.html!")
