import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time
from fpdf import FPDF
import argparse
import re
import random

class WebCrawler:
    def __init__(self, start_url, max_depth=3, same_domain_only=True, retry_count=3):
        self.start_url = start_url
        self.max_depth = max_depth
        self.same_domain_only = same_domain_only
        self.visited_urls = set()
        self.to_visit = [(start_url, 0)]  # (url, depth)
        self.scraped_data = {}
        self.base_domain = urlparse(start_url).netloc
        self.retry_count = retry_count
        
        # List of common user agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
    def is_valid_url(self, url):
        """Check if URL should be crawled based on filters"""
        if not url or url in self.visited_urls:
            return False
            
        # Filter out common non-HTML content
        if any(url.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.mp4', '.mp3']):
            return False
        
        # Filter out javascript:void(0) and similar
        if url.startswith('javascript:') or url.startswith('mailto:') or url.startswith('tel:'):
            return False
            
        # Check if URL is from the same domain if that filter is enabled
        if self.same_domain_only:
            parsed_url = urlparse(url)
            if parsed_url.netloc and parsed_url.netloc != self.base_domain:
                return False
                
        return True
        
    def clean_text(self, text):
        """Clean up the scraped text"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    def get_random_headers(self):
        """Generate random browser-like headers"""
        user_agent = random.choice(self.user_agents)
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
    def scrape_page(self, url):
        """Scrape content from a single page with retry logic"""
        for attempt in range(self.retry_count):
            try:
                # Add a slightly random delay to mimic human behavior
                delay = 2 + random.uniform(1, 3)
                time.sleep(delay)
                
                headers = self.get_random_headers()
                response = requests.get(url, timeout=15, headers=headers)
                response.raise_for_status()  # Raise exception for 4XX/5XX responses
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract the main content (adjust selectors based on website structure)
                # This is a simple example, you may need to customize this for specific sites
                title = soup.title.text.strip() if soup.title else "No Title"
                
                # Try to get the main content
                main_content = ""
                # Look for common content containers
                content_elements = soup.select('main, article, .content, #content, .post, .section, .doc')
                
                if content_elements:
                    for element in content_elements:
                        main_content += element.get_text(strip=True) + "\n\n"
                else:
                    # Fallback to body content with some filtering
                    body = soup.body
                    if body:
                        # Remove script, style, header, footer, nav elements
                        for tag in body.select('script, style, header, footer, nav, aside, .sidebar'):
                            tag.decompose()
                        main_content = body.get_text(strip=True)
                
                main_content = self.clean_text(main_content)
                
                # Find all links on the page
                links = []
                for a_tag in soup.find_all('a', href=True):
                    link = a_tag['href']
                    # Convert relative URLs to absolute
                    absolute_link = urljoin(url, link)
                    if self.is_valid_url(absolute_link):
                        links.append(absolute_link)
                        
                return {
                    'title': title,
                    'content': main_content,
                    'links': links
                }
                
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt+1}/{self.retry_count} failed for {url}: {e}")
                if attempt == self.retry_count - 1:  # If this was the last attempt
                    print(f"All retry attempts failed for {url}")
                    return {
                        'title': f"Error: {url}",
                        'content': f"Failed to scrape after {self.retry_count} attempts: {str(e)}",
                        'links': []
                    }
                # Wait longer between retries
                time.sleep(5 + random.uniform(0, 5))
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                return {
                    'title': f"Error: {url}",
                    'content': f"Failed to scrape: {str(e)}",
                    'links': []
                }
            
    def crawl(self):
        """Crawl websites starting from the start URL"""
        total_urls = len(self.to_visit)
        pbar = tqdm(total=total_urls, desc="Crawling websites")
        
        while self.to_visit:
            current_url, depth = self.to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            pbar.update(1)
            
            print(f"Crawling: {current_url} (Depth: {depth}/{self.max_depth})")
            
            # Skip if we're beyond max depth
            if depth > self.max_depth:
                continue
                
            # Scrape the page
            page_data = self.scrape_page(current_url)
            self.scraped_data[current_url] = {
                'title': page_data['title'],
                'content': page_data['content'],
                'depth': depth
            }
            
            # Add new links to visit
            new_links = 0
            for link in page_data['links']:
                if link not in self.visited_urls and (link, depth+1) not in self.to_visit:
                    self.to_visit.append((link, depth+1))
                    new_links += 1
                    
            # Update progress bar with new total
            if new_links > 0:
                total_urls += new_links
                pbar.total = total_urls
                pbar.refresh()
            
        pbar.close()
        print(f"Crawling completed. Visited {len(self.visited_urls)} pages.")
        
    def export_to_pdf(self, filename="scraped_data.pdf"):
        """Export scraped data to a PDF file"""
        print("Generating PDF...")
        
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Add title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Scraped Data from {self.start_url}", ln=True)
        pdf.ln(10)
        
        # Add summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Summary", ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, f"Total pages scraped: {len(self.scraped_data)}", ln=True)
        pdf.cell(0, 10, f"Maximum depth: {self.max_depth}", ln=True)
        pdf.ln(10)
        
        # Create a table of contents
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Table of Contents", ln=True)
        pdf.ln(5)
        
        # Sort URLs by depth for better organization
        sorted_urls = sorted(self.scraped_data.items(), key=lambda x: (x[1]['depth'], x[0]))
        
        pdf.set_font("Arial", '', 10)
        for i, (url, data) in enumerate(sorted_urls):
            # Truncate long URLs
            display_url = url if len(url) < 80 else url[:77] + "..."
            pdf.cell(0, 10, f"{i+1}. {data['title']} (Depth: {data['depth']})", ln=True)
        
        pdf.add_page()
        
        # Add content for each page
        for i, (url, data) in enumerate(tqdm(sorted_urls, desc="Creating PDF")):
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, f"{i+1}. {data['title']}", ln=True)
            
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, f"URL: {url}", ln=True)
            pdf.cell(0, 10, f"Depth: {data['depth']}", ln=True)
            
            pdf.set_font("Arial", '', 10)
            
            # Split content into smaller chunks to avoid FPDF errors with large text
            content_chunks = [data['content'][i:i+5000] for i in range(0, len(data['content']), 5000)]
            for chunk in content_chunks:
                # Handle errors that might occur with special characters
                try:
                    pdf.multi_cell(0, 10, chunk)
                except Exception as e:
                    pdf.multi_cell(0, 10, f"[Error displaying content: {str(e)}]")
                
            pdf.ln(10)
            
            # Add a new page if not the last item
            if i < len(sorted_urls) - 1:
                pdf.add_page()
                
        pdf.output(filename)
        print(f"PDF saved as {filename}")

def main():
    parser = argparse.ArgumentParser(description='Web crawler and scraper with PDF export')
    parser.add_argument('url', help='Starting URL to crawl')
    parser.add_argument('--depth', type=int, default=2, help='Maximum crawling depth (default: 2)')
    parser.add_argument('--output', default='scraped_data.pdf', help='Output PDF filename')
    parser.add_argument('--same-domain', action='store_true', help='Only crawl pages from the same domain')
    parser.add_argument('--retries', type=int, default=3, help='Number of retry attempts for failed requests')
    
    args = parser.parse_args()
    
    crawler = WebCrawler(args.url, max_depth=args.depth, same_domain_only=args.same_domain, retry_count=args.retries)
    crawler.crawl()
    crawler.export_to_pdf(args.output)

if __name__ == "__main__":
    main()