import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
import time
import os
import sys
import requests
from bs4 import BeautifulSoup
import random
from urllib.parse import urljoin, urlparse
import re

class WebCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler (One-Big-HTML PDF Export)")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Try setting a window icon (optional)
        try:
            self.root.iconbitmap("spider.ico")
        except:
            pass
            
        # Variables
        self.url_var = tk.StringVar()
        self.depth_var = tk.IntVar(value=2)
        self.output_var = tk.StringVar(value="scraped_data.pdf")
        self.same_domain_var = tk.BooleanVar(value=True)
        self.retry_var = tk.IntVar(value=3)
        self.crawler_thread = None
        self.is_running = False
        
        # Create GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Crawler Settings", padding="10")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # URL input
        ttk.Label(input_frame, text="URL to Crawl:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(input_frame, textvariable=self.url_var, width=60).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Depth input
        ttk.Label(input_frame, text="Max Depth:").grid(row=1, column=0, sticky=tk.W, pady=5)
        depth_spinner = ttk.Spinbox(input_frame, from_=1, to=10, textvariable=self.depth_var, width=5)
        depth_spinner.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Retry input
        ttk.Label(input_frame, text="Retry Count:").grid(row=2, column=0, sticky=tk.W, pady=5)
        retry_spinner = ttk.Spinbox(input_frame, from_=0, to=10, textvariable=self.retry_var, width=5)
        retry_spinner.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Output file input
        ttk.Label(input_frame, text="Output PDF:").grid(row=3, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(input_frame)
        output_frame.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output).pack(side=tk.RIGHT, padx=5)
        
        # Same domain checkbox
        ttk.Checkbutton(input_frame, text="Stay in Same Domain", variable=self.same_domain_var).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.start_button = ttk.Button(button_frame, text="Start Crawling", command=self.start_crawling)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_crawling, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.status_var).pack(anchor=tk.W, padx=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.output_var.set(filename)
    
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.status_var.set(message)
        self.status_bar.config(text=message)
    
    def start_crawling(self):
        """Start the crawler in a separate thread"""
        url = self.url_var.get()
        if not url:
            self.log("Error: Please enter a URL")
            return
            
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'https://' + url
            self.url_var.set(url)
            
        self.log(f"Starting crawler with URL: {url}")
        self.progress_var.set(0)
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start in a new thread
        self.crawler_thread = threading.Thread(target=self.run_crawler)
        self.crawler_thread.daemon = True
        self.crawler_thread.start()
    
    def stop_crawling(self):
        """Stop the crawler"""
        if self.is_running:
            self.is_running = False
            self.log("Stopping crawler (this may take a moment)...")
            self.stop_button.config(state=tk.DISABLED)
    
    def run_crawler(self):
        """Run the crawler"""
        try:
            url = self.url_var.get()
            depth = self.depth_var.get()
            output = self.output_var.get()
            same_domain = self.same_domain_var.get()
            retries = self.retry_var.get()
            
            crawler = WebCrawler(
                url, 
                max_depth=depth, 
                same_domain_only=same_domain, 
                retry_count=retries,
                gui_callback=self.log,
                progress_callback=self.update_progress
            )
            
            if self.is_running:
                self.log("Starting to crawl web pages...")
                crawler.crawl()
                
                if self.is_running:
                    self.log("Crawling completed. Creating single big HTML and exporting to PDF...")
                    crawler.export_to_pdf(output)
                    self.log(f"PDF saved as {output}")
                    
                    # Try to open the folder containing the PDF
                    try:
                        folder_path = os.path.dirname(os.path.abspath(output))
                        if sys.platform == 'win32':
                            os.startfile(folder_path)
                        elif sys.platform == 'darwin':  # macOS
                            import subprocess
                            subprocess.Popen(['open', folder_path])
                        else:  # Linux
                            import subprocess
                            subprocess.Popen(['xdg-open', folder_path])
                    except:
                        pass
        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_var.set("Ready")
            self.status_bar.config(text="Ready")
    
    def update_progress(self, current, total):
        """Update progress bar"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
            self.root.update_idletasks()


class WebCrawler:
    def __init__(self, start_url, max_depth=3, same_domain_only=True, retry_count=3, 
                 gui_callback=None, progress_callback=None):
        self.start_url = start_url
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.visited_urls = set()
        self.to_visit = [(start_url, 0)]  # (url, depth)
        
        # We'll store raw HTML for each page so we can build one big doc
        self.scraped_data = {}  # { url: { 'title': ..., 'html': ..., 'depth': ... } }
        
        self.base_domain = urlparse(start_url).netloc
        self.retry_count = retry_count
        self.gui_callback = gui_callback  # Function to update GUI
        self.progress_callback = progress_callback  # Function to update progress
        self.stop_requested = False
        
        # Common user agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
    
    def log(self, message):
        """Log message to GUI if callback is provided"""
        if self.gui_callback:
            self.gui_callback(message)
        else:
            print(message)
            
    def is_valid_url(self, url):
        """Check if URL should be crawled based on filters"""
        if not url or url in self.visited_urls:
            return False
            
        # Filter out common non-HTML content
        if any(url.lower().endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.mp4', '.mp3', '.jpeg', '.svg']):
            return False
        
        # Filter out javascript:, mailto:, tel:
        if url.startswith('javascript:') or url.startswith('mailto:') or url.startswith('tel:'):
            return False
            
        # Check if URL is from the same domain if that filter is enabled
        if self.same_domain_only:
            parsed_url = urlparse(url)
            if parsed_url.netloc and parsed_url.netloc != self.base_domain:
                return False
                
        return True
        
    def get_random_headers(self):
        """Generate random browser-like headers"""
        user_agent = random.choice(self.user_agents)
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
    def scrape_page(self, url):
        """Scrape a page (including raw HTML) with retry logic"""
        for attempt in range(self.retry_count):
            try:
                # Add random delay
                delay = 1 + random.uniform(0.5, 1.5)
                time.sleep(delay)
                
                headers = self.get_random_headers()
                self.log(f"Requesting {url} (Attempt {attempt+1}/{self.retry_count})")
                response = requests.get(url, timeout=15, headers=headers)
                response.raise_for_status()
                
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                title = soup.title.text.strip() if soup.title else "No Title"
                self.log(f"Processing: {title}")
                
                # Find all valid links for the crawler
                links = []
                for a_tag in soup.find_all('a', href=True):
                    link = a_tag['href']
                    absolute_link = urljoin(url, link)
                    if self.is_valid_url(absolute_link):
                        links.append(absolute_link)
                
                self.log(f"Found {len(links)} valid links on {url}")
                        
                return {
                    'title': title,
                    'html': html_content,
                    'links': links
                }
                
            except requests.exceptions.RequestException as e:
                self.log(f"Attempt {attempt+1}/{self.retry_count} failed for {url}: {e}")
                if attempt == self.retry_count - 1:
                    self.log(f"All retry attempts failed for {url}")
                    return {
                        'title': f"Error: {url}",
                        'html': f"<h1>Failed after {self.retry_count} attempts: {e}</h1>",
                        'links': []
                    }
                time.sleep(2 + random.uniform(0, 2))
            except Exception as e:
                self.log(f"Error scraping {url}: {e}")
                return {
                    'title': f"Error: {url}",
                    'html': f"<h1>Failed to scrape: {e}</h1>",
                    'links': []
                }
            
    def crawl(self):
        """Crawl websites starting from the start URL"""
        total_urls = len(self.to_visit)
        processed_urls = 0
        
        while self.to_visit and not self.stop_requested:
            current_url, depth = self.to_visit.pop(0)
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            processed_urls += 1
            
            # Update progress
            if self.progress_callback:
                self.progress_callback(processed_urls, total_urls)
                
            self.log(f"Crawling: {current_url} (Depth: {depth}/{self.max_depth})")
            
            # Skip if we're beyond max depth
            if depth > self.max_depth:
                continue
                
            # Scrape the page
            page_data = self.scrape_page(current_url)
            self.scraped_data[current_url] = {
                'title': page_data['title'],
                'html': page_data['html'],
                'depth': depth
            }
            
            # Enqueue new links
            new_links = 0
            for link in page_data['links']:
                if link not in self.visited_urls and (link, depth+1) not in self.to_visit:
                    self.to_visit.append((link, depth+1))
                    new_links += 1
                    
            if new_links > 0:
                total_urls += new_links
                self.log(f"Added {new_links} new URLs to the queue. Total: {total_urls}")
            
        if self.stop_requested:
            self.log("Crawling stopped by user")
        else:
            self.log(f"Crawling completed. Visited {len(self.visited_urls)} pages.")
        
        # Final progress update
        if self.progress_callback:
            self.progress_callback(processed_urls, total_urls)
    
    def export_to_pdf(self, filename="scraped_data.pdf"):
        """
        Build a single big HTML containing all pages, rewriting internal links 
        to in-document anchors, then generate ONE PDF via Playwright.
        """
        self.log("Generating one big HTML document from crawled pages...")
        big_html = self.build_big_html()
        
        self.log("Rendering combined HTML to PDF via Playwright (this might take a moment)...")
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Set the combined HTML content
            page.set_content(big_html, wait_until="networkidle")
            
            # Export to PDF
            page.pdf(path=filename, format="A4", print_background=True)
            browser.close()
        
        self.log(f"PDF saved as {filename}")

    def build_big_html(self):
        """
        Build a single HTML doc with:
          - A table of contents linking to each page's anchor
          - Each page's HTML in a <section> with an <a name="..."> anchor
          - Internal links pointing to #anchors instead of external URLs
        """
        from bs4 import BeautifulSoup

        # Sort URLs by depth (and alphabetically for stability)
        sorted_items = sorted(self.scraped_data.items(), key=lambda x: (x[1]['depth'], x[0]))
        
        # Create a mapping from URL -> anchor_id
        anchor_map = {}
        for i, (url, data) in enumerate(sorted_items):
            anchor_map[url] = f"page_{i}"
        
        # Build a table of contents
        html_output = [
            "<html><head>",
            "<meta charset='utf-8'/>",
            "<title>Crawled Data</title></head><body>",
            "<h1>Table of Contents</h1><ul>"
        ]
        
        for url, data in sorted_items:
            anchor_id = anchor_map[url]
            title = data['title']
            # Link to the anchor
            html_output.append(f'<li><a href="#{anchor_id}">{title}</a></li>')
        html_output.append("</ul><hr>")
        
        # Build sections for each page
        for url, data in sorted_items:
            anchor_id = anchor_map[url]
            # Original raw HTML
            raw_html = data['html']
            
            # Parse so we can rewrite links
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            # Rewrite links that point to other crawled pages => #some_anchor
            for a_tag in soup.find_all('a', href=True):
                link = a_tag['href']
                full_link = urljoin(url, link)
                if full_link in anchor_map:
                    a_tag['href'] = f"#{anchor_map[full_link]}"
            
            # Add a heading with anchor
            html_output.append(f'<section><a name="{anchor_id}"></a>')
            html_output.append(f'<h2>{data["title"]}</h2>')
            
            # Ideally, remove <script>, etc., or keep them for styling if needed
            # We'll just keep the entire <body> for a near-original look:
            # If the site is huge, consider removing repeated <header>, <footer>, etc.
            # But let's keep it simple:
            
            # Insert the body or entire soup
            body = soup.body
            if body:
                # The <body> content only
                html_output.append(str(body))
            else:
                # Fallback: the entire HTML if <body> not found
                html_output.append(raw_html)
            
            html_output.append("</section><hr>")
        
        html_output.append("</body></html>")
        return "\n".join(html_output)


def main():
    root = tk.Tk()
    app = WebCrawlerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
