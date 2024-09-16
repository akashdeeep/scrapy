from pathlib import Path
import scrapy
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
import json
from tqdm import tqdm

load_dotenv()


class SAPOTCSpider(scrapy.Spider):
    name = "sap_otc_spider"

    def __init__(self, start_urls=None, depth=2, *args, **kwargs):
        super(SAPOTCSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = start_urls.split(",")
        self.custom_depth = int(depth)
        self.processed = set()
        self.pages_crawled = 0
        self.total_pages = 1
        self.pbar = tqdm(
            total=self.total_pages,
            desc="Crawling progress",
            bar_format="{l_bar}{bar}{r_bar}",
        )

    def start_requests(self):
        """Start requests from the provided start URLs."""
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        """Main parsing method that processes each page and follows links."""

        self.pages_crawled += 1
        self.log_progress()

        page_content = response.body
        cleaned_page = self.extract_text(page_content)

        if (response.url in self.processed) or (
            response.meta.get("depth", 0) >= self.custom_depth
        ):
            return
        self.processed.add(response.url)

        self.save_page(response, cleaned_page)

        for next_page in response.css("a::attr(href)").getall():
            if next_page is not None:

                self.total_pages += 1
                self.pbar.total = self.total_pages
                self.pbar.refresh()
                yield response.follow(next_page, callback=self.parse)

    def extract_text(self, html_content):
        """Extracts visible text from the HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text(separator=" ")
        cleaned_text = " ".join(text.split())
        return cleaned_text

    def save_page(self, response, cleaned_page):
        """Saves the cleaned page content along with metadata to a JSON file."""

        cleaned_url = (
            response.url.replace("https://", "").replace(".com", "").replace("/", "-")
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        depth = response.meta.get("depth", 0)

        directory = "files_crawled"
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = f"{directory}/{cleaned_url}_depth{depth}_{timestamp}.json"
        metadata = {
            "url": response.url,
            "depth": depth,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        file_data = {
            "metadata": metadata,
            "content": cleaned_page,
        }

        with open(file_name, "w") as json_file:
            json.dump(file_data, json_file, indent=4)

    def log_progress(self):
        """Logs the current progress of the crawl and updates the tqdm progress bar."""
        self.pbar.update(1)
        progress = (
            (self.pages_crawled / self.total_pages) * 100 if self.total_pages > 0 else 0
        )
        self.logger.info(
            f"Progress: {self.pages_crawled}/{self.total_pages} pages crawled ({progress:.2f}% complete)"
        )

    def closed(self, reason):
        """Closes the progress bar when the spider is done."""
        if self.pbar is not None:
            self.pbar.close()
