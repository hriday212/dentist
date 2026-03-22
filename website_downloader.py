import os
import sys
import requests
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pathlib import Path
import re
from playwright.async_api import async_playwright

def get_base_domain(url):
    """Simple heuristic to get the primary domain, e.g., 'blog.example.com' -> 'example.com'"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    parts = domain.split('.')
    multi_part_suffixes = {'co.uk', 'org.uk', 'gov.uk', 'ac.uk', 'com.au', 'net.au', 'org.au', 'co.in', 'org.in', 'net.in'}
    if len(parts) >= 3:
        last_two = ".".join(parts[-2:])
        if last_two in multi_part_suffixes:
            return ".".join(parts[-3:])
        return last_two
    return domain

class WebsiteDownloader:
    def __init__(self, start_url, output_dir, max_depth=2, max_workers=10, blog_sample_limit=1):
        self.start_url = start_url
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.max_workers = max_workers
        self.blog_sample_limit = blog_sample_limit
        
        self.visited = set()
        self.blog_samples_count = {} 
        self.download_count = 0
        self.error_count = 0
        
        self.blog_path_segments = ['/blog/', '/post/', '/posts/', '/article/', '/articles/', '/p/']
        self.base_domain = get_base_domain(start_url)
        
        self.session = requests.Session()
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        self.session.headers.update({'User-Agent': self.user_agent})
        
        print(f"Targeting: *.{self.base_domain}")
        print(f"Recursion depth limit: {self.max_depth}")
        print(f"Blog samples per pattern: {self.blog_sample_limit}")
        print(f"Saving to: {self.output_dir.absolute()}")

    def _get_blog_pattern(self, url):
        path = urlparse(url).path.lower()
        for segment in self.blog_path_segments:
            if segment in path and path.strip('/').split('/')[-1] != "":
                return segment
        return None

    def is_internal(self, url):
        domain = urlparse(url).netloc.lower()
        return domain == self.base_domain or domain.endswith('.' + self.base_domain)

    def get_local_path(self, url):
        parsed = urlparse(url)
        netloc = parsed.netloc
        path = parsed.path
        
        if not path or path.endswith('/'):
            path = os.path.join(path, 'index.html')
        elif not os.path.splitext(path)[1]: 
            path = os.path.join(path, 'index.html')
        
        sanitized_path = re.sub(r'[\\:*?"<>|]', '_', path)
        return self.output_dir / netloc / sanitized_path.lstrip('/')

    def _get_sitemap_urls(self):
        sitemap_urls = set()
        robots_url = urljoin(self.start_url, '/robots.txt')
        try:
            resp = self.session.get(robots_url, timeout=10)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        print(f"Found sitemap in robots.txt: {sitemap_url}")
                        sitemap_urls.update(self._parse_sitemap(sitemap_url))
        except Exception:
            pass

        if not sitemap_urls:
            default_sitemap = urljoin(self.start_url, '/sitemap.xml')
            print(f"Checking default sitemap location: {default_sitemap}")
            sitemap_urls.update(self._parse_sitemap(default_sitemap))
        return sitemap_urls

    def _parse_sitemap(self, sitemap_url):
        urls = set()
        try:
            resp = self.session.get(sitemap_url, timeout=10)
            if resp.status_code == 200:
                if 'xml' in resp.headers.get('Content-Type', '').lower() or sitemap_url.endswith('.xml'):
                    soup = BeautifulSoup(resp.content, 'html.parser')
                    for loc in soup.find_all('loc'):
                        loc_url = loc.text.strip()
                        if loc_url.endswith('.xml'):
                            print(f"Found sitemap index: {loc_url}")
                            urls.update(self._parse_sitemap(loc_url))
                        elif self.is_internal(loc_url):
                            urls.add(loc_url)
        except Exception as e:
            print(f"Failed to parse sitemap {sitemap_url}: {e}")
        return urls

    def _download_asset_requests(self, url):
        """Fallback to requests for binary/static files."""
        try:
            response = self.session.get(url, timeout=15, stream=True)
            if response.status_code != 200:
                return None
            local_path = self.get_local_path(url)
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
            return ('asset', url, None)
        except Exception:
            return None

    async def _download_resource(self, url, browser_context, semaphore):
        async with semaphore:
            if url in self.visited:
                return None
            self.visited.add(url)
            
            ext = os.path.splitext(urlparse(url).path)[1].lower()
            if ext and ext not in ['.html', '.php', '.asp', '.aspx']:
                # It has a distinct non-html extension, use requests 
                # (e.g. .css, .js, .png, .jpg)
                res = await asyncio.to_thread(self._download_asset_requests, url)
                if res is not None:
                    self.download_count += 1
                return res
            
            # Treat as HTML, use playwright
            try:
                page = await browser_context.new_page()
                # Wait for network responses to drop to 0, meaning React has rendered
                response = await page.goto(url, wait_until="networkidle", timeout=25000)
                
                # If page is missing
                if response and not response.ok:
                    self.error_count += 1
                    print(f"Skipping {url} (HTTP {response.status})")
                    await page.close()
                    return None
                
                content = await page.content()
                await page.close()
                
                local_path = self.get_local_path(url)
                local_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(local_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
                
                self.download_count += 1
                return ('html', url, content)
                    
            except Exception as e:
                self.error_count += 1
                print(f"Error rendering {url}: {e}")
                return None

    async def start_download_async(self):
        queue = [(self.start_url, 0)]
        sitemap_urls = self._get_sitemap_urls()
        
        if sitemap_urls:
            print(f"Found {len(sitemap_urls)} URLs from sitemap(s).")
            for url in sitemap_urls:
                if url != self.start_url:
                    queue.append((url, 1))
        
        async with async_playwright() as p:
            print("Launching headless browser...")
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(user_agent=self.user_agent)
            
            # Concurrency limit to prevent overloading browser / memory
            semaphore = asyncio.Semaphore(self.max_workers)
            
            while queue:
                current_batch = queue
                queue = []
                
                depth = current_batch[0][1]
                print(f"\n--- BFS Level {depth} | {len(current_batch)} URLs in queue ---")
                
                tasks = [self._download_resource(url, context, semaphore) for url, _ in current_batch]
                results = await asyncio.gather(*tasks)
                
                for i, result in enumerate(results):
                    if not result: continue
                    res_type, original_url, content = result
                    
                    if res_type == 'html' and current_batch[i][1] < self.max_depth:
                        soup = BeautifulSoup(content, 'html.parser')
                        tags_attrs = [('a', 'href'), ('link', 'href'), ('script', 'src'), ('img', 'src')]
                        
                        for tag_name, attr in tags_attrs:
                            for tag in soup.find_all(tag_name, **{attr: True}):
                                link = tag.get(attr)
                                abs_link = urljoin(original_url, link).split('#')[0]
                                
                                if any(abs_link.lower().startswith(p) for p in ['mailto:', 'tel:', 'javascript:', 'data:']):
                                    continue
                                    
                                if self.is_internal(abs_link) and abs_link not in self.visited:
                                    pattern = self._get_blog_pattern(abs_link)
                                    if pattern:
                                        count = self.blog_samples_count.get(pattern, 0)
                                        if count >= self.blog_sample_limit:
                                            continue
                                        self.blog_samples_count[pattern] = count + 1
                                    
                                    if not any(item[0] == abs_link for item in queue):
                                        queue.append((abs_link, depth + 1))
            
            await browser.close()
            
        print(f"\n{'='*40}")
        print(f"Download complete!")
        print(f"Total files rendered/saved: {self.download_count}")
        print(f"Errors encountered: {self.error_count}")
        print(f"{'='*40}")

if __name__ == "__main__":
    url_to_download = sys.argv[1] if len(sys.argv) > 1 else input("Enter URL (e.g., example.com): ")
    if not url_to_download.startswith("http"):
        url_to_download = "https://" + url_to_download
        
    # Lower max_workers for Playwright to avoid out-of-memory or too many browser tabs
    downloader = WebsiteDownloader(url_to_download, "downloaded_site", max_depth=2, max_workers=5)
    asyncio.run(downloader.start_download_async())
    print("\nSummary: Check 'downloaded_site' folder for your offline copy.")
