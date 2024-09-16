from pathlib import Path
import scrapy
import openai
import os
from dotenv import load_dotenv
from conf import llm
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import json

load_dotenv()


class SAPOTCSpider(scrapy.Spider):
    name = "sap_otc_spider"

    start_urls = [
        "https://community.sap.com/t5/enterprise-resource-planning-blogs-by-members/sap-order-to-cash-process-sd/ba-p/13551270",
        "https://techconcepthub.com/otc-process-in-sap/",
    ]

    processed = set()

    def parse(self, response):

        page_content = response.body
        cleaned_page = self.extract_text(page_content)

        if (response.url in self.processed) or (response.meta.get("depth", 0) >= 2):
            return
        metadata = {
            "url": response.url,
            "depth": response.meta.get("depth", 0),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.processed.add(response.url)
        print(response.url, response.meta.get("depth"))
        if response.meta.get("depth", 0) == 0:
            is_relevant = True
        else:
            is_relevant = True

        if is_relevant:
            directory = "files_crawled"
            # Ensure the directory exists before writing the file
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_name = f"{directory}/{response.url.split('/')[-2]}.json"
            file_data = {
                "metadata": metadata,
                "content": cleaned_page,
            }
            # Save the file as JSON
            with open(file_name, "w") as json_file:
                json.dump(file_data, json_file, indent=4)

            for next_page in response.css("a::attr(href)").getall():
                if next_page is not None:
                    yield response.follow(next_page, callback=self.parse)

    def extract_text(self, html_content):
        """Extracts visible text from the HTML content using BeautifulSoup."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Extract visible text
        text = soup.get_text(separator=" ")

        # Clean up the text (remove extra spaces, newlines, etc.)
        cleaned_text = " ".join(text.split())
        return cleaned_text
