
# 🕸️ Web Crawler (GUI) with Styled PDF Export

A robust Python web crawler that recursively visits links, scrapes content, and exports all pages into a **single, styled PDF**. The GUI provides a user-friendly way to input your starting URL, maximum depth, and export file. The final PDF is rendered by **Playwright**—preserving images, CSS, and layout for each crawled page.

## ✨ Features

- **🔄 Recursive Web Crawling**  
  Follows links on each page up to a specified depth, with an option to stay in the same domain.  

- **📊 Progress Tracking**  
  Includes a real-time progress bar showing how many pages have been crawled out of the total queue.  

- **🖥️ GUI Interface**  
  Simple Tkinter-based interface: just enter the starting URL, choose options, and click **Start**.  

- **📑 Single PDF Export (via Playwright)**  
  Merges the content from all crawled pages into **one** PDF document while preserving original webpage styling.  

- **🛡️ Robust Error Handling**  
  Retries failed requests and logs errors so the crawler can continue.  

- **🌐 Browser Simulation**  
  The crawler rotates user agents to reduce the likelihood of blocks and suspicious activity.  

## 🚀 Installation

### Prerequisites

- **Python 3.7+**  
- **pip** (Python package installer)  
- **Playwright** and **Browsers**  

### Setup

1. **Clone this repository** or download the source code:
   ```bash
   git clone https://github.com/hatimc21/web_crawler.git
   cd web_crawler
   ```

2. *(Optional but recommended)* **Create a virtual environment**:
   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment**:
   - **Windows**: `env\Scripts\activate`
   - **macOS/Linux**: `source env/bin/activate`

4. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
   Make sure your `requirements.txt` includes:
   ```
   requests
   beautifulsoup4
   playwright
   PyPDF2
   ```
   Then install the Playwright browsers:
   ```bash
   playwright install
   ```

## 🔧 Usage

1. **Run the GUI**:
   ```bash
   python web_crawler.py
   ```
2. **Enter your settings**:
   - **URL to Crawl**: e.g. `https://example.com`
   - **Max Depth**: how many link levels to follow
   - **Retry Count**: how many times to retry a failing page
   - **Same Domain**: whether to only follow links on the same domain
   - **Output PDF**: path to save the final PDF file

3. **Click "Start Crawling"** to begin.
4. **Watch the progress bar** update as pages are crawled.
5. After crawling finishes, the script will generate a **single PDF** combining all pages.

### How Does the PDF Export Work?

1. The crawler collects **raw HTML** from each page.
2. A **big HTML document** is compiled, with each page placed into a separate `<section>`.
3. **Internal links** between crawled pages are rewritten into **in-document anchors** (e.g. `#page_3`) rather than external URLs.
4. **Playwright** launches a headless Chromium to render that combined HTML into a visually styled PDF.

## ⚠️ Limitations

- **JavaScript for Crawling**: The crawler itself uses `requests` + `BeautifulSoup`, so dynamically rendered content might not appear in the scraped HTML.  
- **Anchor Links in PDF**: Some PDF viewers do not natively treat HTML anchor links as internal “GoTo” references. Clicking an internal link may open your browser instead of jumping to another section in the PDF.
- **Large Websites**: Crawling a very large site to a high depth can produce huge PDFs. Use depth filters to limit scope.

## 🔍 Ethical Use

- **Respect robots.txt** and websites’ terms of service.  
- **Obtain permission** before crawling websites that you do not own.  
- Use for **legitimate** purposes (archiving, documentation, personal research).

## 📜 License

[MIT License](LICENSE)

