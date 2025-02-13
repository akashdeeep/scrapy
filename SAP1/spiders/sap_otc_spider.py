from pathlib import Path
import scrapy
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
import json
import scrapy.exceptions
from tqdm import tqdm
import requests
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

load_dotenv()


def is_allowed_by_robots(url):
    """Checks if a URL is allowed to be crawled based on robots.txt."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    rp = RobotFileParser()
    rp.set_url(robots_url)

    try:
        rp.read()
        return rp.can_fetch("*", url)  # "*" checks for any user agent
    except:
        return True  # If robots.txt is unavailable, assume allowed


class SAPOTCSpider(scrapy.Spider):
    name = "sap_otc_spider"

    def __init__(self, start_urls=None, depth=2, *args, **kwargs):
        super(SAPOTCSpider, self).__init__(*args, **kwargs)
        if start_urls:
            self.start_urls = list(set(start_urls.split(",")))
        self.custom_depth = int(depth)
        self.processed = set()
        self.pages_crawled = 0
        self.counted = set()
        self.forbidden = set()

        for url in self.start_urls:
            if not is_allowed_by_robots(url):
                self.forbidden.add(url)
            else:
                self.counted.add(url)
        self.total_pages = len(self.counted)
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
        if response.status == 403:
            self.pages_crawled += 1
            self.forbidden.add(response.url)
            self.log_progress()
            print(f"link {response.url} is forbidden")
            return
        if (response is None) or (response.body is None):
            self.pages_crawled += 1
            self.processed.add(response.url)
            self.log_progress()
            print(f"link {response.url} is broken")
            return

        self.pages_crawled += 1
        self.processed.add(response.url)
        self.log_progress()

        page_content = response.body
        cleaned_page = self.extract_text(page_content)
        self.save_page(response, cleaned_page)

        if response.meta.get("depth", 0) < self.custom_depth:
            for link in response.css("a::attr(href)").getall():
                full_link = (
                    response.urljoin(link) if not link.startswith("http") else link
                )
                if not is_allowed_by_robots(full_link):
                    self.forbidden.add(full_link)
                    continue
                self.counted.add(full_link)
                yield response.follow(
                    full_link,
                    self.parse,
                    meta={"depth": response.meta.get("depth", 0) + 1},
                )

    def handle_error(self, failure):
        """Handles errors that occur during the crawling process."""
        request = failure.request
        if failure.check(scrapy.exceptions.IgnoreRequest):
            self.forbidden.add(request.url)
            self.pages_crawled += 1
            self.log_progress()

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

        file_name = f"{directory}/{cleaned_url}.json"
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
        self.total_pages = len(self.counted)
        self.pages_crawled = len(self.processed)
        progress = (
            (self.pages_crawled / self.total_pages) * 100 if self.total_pages > 0 else 0
        )
        self.logger.info(
            f"Progress: {self.pages_crawled}/{self.total_pages} pages crawled ({progress:.2f}% complete)"
        )
        self.pbar.total = self.total_pages
        self.pbar.update(1)

    def closed(self, reason):
        """Closes the progress bar when the spider is done and logs uncrawled URLs."""
        if self.pbar is not None:
            self.pbar.close()

        uncrawled_urls = self.counted - self.processed
        # uncrawled_urls.update(self.forbidden)

        if uncrawled_urls:
            self.logger.info(f"Uncrawled URLs ({len(uncrawled_urls)}):")
            for url in uncrawled_urls:
                self.logger.info(url)

            # Save the uncrawled URLs to a file for further inspection
            with open("uncrawled_urls.txt", "w") as f:
                f.writelines("\n".join(uncrawled_urls))

            self.logger.info("List of uncrawled URLs saved to 'uncrawled_urls.txt'.")

        if self.forbidden:
            self.logger.info(f"Forbidden URLs ({len(self.forbidden)}):")
            for url in self.forbidden:
                self.logger.info(url)

            with open("forbidden_urls.txt", "w") as f:
                f.writelines("\n".join(self.forbidden))
            self.logger.info("List of forbidden URLs saved to 'forbidden_urls.txt'.")

        self.logger.info(f"Total pages counted: {len(self.counted)}")
        self.logger.info(f"Total pages crawled: {len(self.processed)}")
        self.logger.info(f"Difference (uncrawled): {len(uncrawled_urls)}")

    def on_bytes_received(self, data, request, spider):
        """Callback for when bytes are received from the server."""

        raise scrapy.exceptions.StopDownload(fail=False)
