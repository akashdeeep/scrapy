# Web Crawler

This repository contains a Scrapy-based web scraper to crawl SAP Order-to-Cash process-related content from the web, extract visible text, and store the data in JSON format for further processing.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [File Structure](#file-structure)
- [License](#license)

## Features

- Scrapes content related to SAP Order-to-Cash (OTC) processes.
- Extracts only the visible text from web pages (ignoring scripts and styles).
- Saves the crawled content along with metadata (URL, crawl depth, timestamp) in a structured JSON format.
- Uses `tqdm` to display a progress bar for the crawling process.
- Depth-controlled crawling (configurable via command-line arguments or environment variables).
- Logs the crawling process into a specified file.

## Requirements

- Python 3.7 or higher
- Scrapy
- BeautifulSoup (bs4)
- TQDM
- Requests
- dotenv (optional, if using `.env` for environment variables)

You can install these dependencies using the following command:

```bash
pip install -r requirements.txt
```

### Sample `requirements.txt`

```plaintext
scrapy
beautifulsoup4
tqdm
requests
python-dotenv
```

## Setup

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/sap-otc-scraper.git
   cd sap-otc-scraper
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Create a `.env` file to store environment variables, such as API keys or other sensitive information:

   ```bash
   touch .env
   ```

   In your `.env` file:

   ```ini
   # Example content (if needed)
   SOME_API_KEY=your_api_key_here
   ```

## Usage

### Running the Scraper

You can run the spider using the provided Bash script `run_spider.sh`. This script accepts two optional parameters:

1. **start_urls**: Comma-separated list of starting URLs to crawl.
2. **depth**: Maximum crawl depth (defaults to 2).

#### Example Usage:

```bash
# With default start URLs and depth
./run_spider.sh

# Custom start URLs and depth
./run_spider.sh "https://example.com/page1,https://example.com/page2" 3
```

Alternatively, you can run the spider directly using Scrapy:

```bash
scrapy runspider SAP1/spiders/sap_otc_spider.py -a start_urls="https://example.com" -a depth=2 -s LOG_FILE=SAP1/logs/otc_spider.log
```

### Logging

The crawler will generate logs at `SAP1/logs/otc_spider.log`. You can inspect the log file to track the spider's activity and troubleshoot any issues.

### Output

- The crawled pages are saved in the `files_crawled/` directory in JSON format, with metadata (URL, timestamp, crawl depth) and cleaned page content.

Each file is named using the URL (with slashes replaced by hyphens) and stored in the following structure:

```plaintext
files_crawled/
│
└── some-website-depth0.json
└── another-website-depth1.json
```

## Configuration

- **Start URLs**: You can customize the start URLs either by editing the Bash script (`run_spider.sh`) or passing them as arguments when running the spider.
- **Depth**: The depth of the crawl can be customized via the `depth` argument passed to the spider. The default depth is set to 2.

## File Structure

```plaintext
sap-otc-scraper/
│
├── SAP1/
│   ├── logs/                 # Directory for log files
│   ├── spiders/              # Directory for Scrapy spiders
│   │   └── sap_otc_spider.py # Main Scrapy spider implementation
├── files_crawled/            # Directory where scraped pages are saved
├── run_spider.sh             # Bash script to run the spider
├── requirements.txt          # Python dependencies
├── .env                      # Optional environment variables
└── README.md                 # Project documentation
```

## License

---

Feel free to modify and adapt this `README.md` file according to your specific needs!
