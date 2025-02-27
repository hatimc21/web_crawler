# 🕸️ Web Crawler with PDF Export 📄

A robust Python web crawler that recursively visits links, scrapes content, and exports the results to a PDF document. The tool includes a progress bar to track crawling status and implements browser-like behavior to minimize blocking.

## ✨ Features

- **🔄 Recursive Web Crawling**: Visits all links on a page and follows them to a specified depth
- **🔒 Domain Filtering**: Option to only crawl pages from the same domain as the starting URL
- **📊 Progress Tracking**: Real-time progress bar showing crawl status
- **📑 PDF Export**: Organizes and saves all scraped content in a structured PDF document
- **🛡️ Robust Error Handling**: Implements retry logic for handling server errors
- **🌐 Browser Simulation**: Rotates user agents and implements realistic browsing patterns

## 🚀 Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

### Setup

1. Clone this repository or download the source code:
```
git clone https://github.com/yourusername/web-crawler.git
cd web-crawler
```

2. It's recommended to create a virtual environment:
```
python -m venv env
```

3. Activate the virtual environment:
   - Windows: `env\Scripts\activate`
   - macOS/Linux: `source env/bin/activate`

4. Install the required packages:
```
pip install requests beautifulsoup4 tqdm fpdf
```

## 🔧 Usage

### Basic Usage

```
python web_crawler.py https://example.com --output results.pdf
```

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `url` | Starting URL to crawl (required) | - |
| `--depth` | Maximum crawling depth | 2 |
| `--output` | Output PDF filename | scraped_data.pdf |
| `--same-domain` | Only crawl pages from the same domain | False |
| `--retries` | Number of retry attempts for failed requests | 3 |

### Examples

Crawl a website to a depth of 3 and save results to "documentation.pdf":
```
python web_crawler.py https://example.com --depth 3 --output documentation.pdf
```

Crawl only pages from the same domain with 5 retry attempts:
```
python web_crawler.py https://example.com --same-domain --retries 5
```

## ⚙️ Customization

The crawler can be customized for specific websites by modifying the `scrape_page` method in the `WebCrawler` class. You may want to adjust the selectors used to extract content based on the structure of the websites you're targeting.

### Scraper Configuration

You can adjust these parameters in the `WebCrawler` class:
- `retry_count`: Number of times to retry failed requests
- `user_agents`: List of user agent strings to rotate between requests

## 🔍 Ethical Use

This tool is designed for legitimate scraping purposes such as:
- 📚 Personal research
- 💾 Archiving documentation
- 📱 Creating offline copies of content you have permission to access

Please ensure you have permission to scrape any website you target and respect robots.txt rules. Using this tool to scrape websites that prohibit automated access may violate terms of service.

## ⚠️ Limitations

- JavaScript-rendered content may not be properly scraped (this uses requests/BeautifulSoup, not a headless browser)
- Some websites may block scraping despite the measures implemented
- PDF output may have formatting limitations for complex content

## 🛠️ Troubleshooting

If you encounter issues with specific websites:

1. **403 Forbidden errors**: The website may be blocking scraping. Try increasing delays or using a more sophisticated approach.
2. **Empty or incomplete content**: The website may use JavaScript to load content. Consider switching to Selenium for such sites.
3. **PDF formatting issues**: For very large pages, try adjusting the chunk size in the `export_to_pdf` method.

## 📜 License

[MIT License](LICENSE)
