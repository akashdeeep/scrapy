from pathlib import Path
import scrapy
import openai  # OpenAI Python client to query the LLM
import os
from dotenv import load_dotenv

load_dotenv()
# Ensure your OpenAI key is set in your environment


class SAPOTCSpider(scrapy.Spider):
    name = "sap_otc_spider"

    # Start with some seed URLs
    start_urls = [
        "https://community.sap.com/t5/enterprise-resource-planning-blogs-by-members/sap-order-to-cash-process-sd/ba-p/13551270",
    ]

    def parse(self, response):
        # Extract the raw page content
        page_content = response.text

        # Ask OpenAI LLM if the page content is related to SAP OTC
        is_relevant = self.is_related_to_sap_otc(page_content)

        if is_relevant:
            # Save the relevant page content locally
            page_title = response.url.split("/")[-2] + ".html"
            Path(page_title).write_text(page_content)

            # Extract the links to crawl recursively
            for next_page in response.css("a::attr(href)").getall():
                if next_page is not None:
                    yield response.follow(next_page, callback=self.parse)

    def is_related_to_sap_otc(self, content):
        # Query OpenAI LLM to check if content is related to SAP Order to Cash
        try:
            prompt = f"""
            Is the following page content related to SAP Order to Cash (OTC)?
            Response: Yes or No
            Do not ask for clarification or context.
            \n\n{content[:2000]}...
            """  # Limit tokens sent to OpenAI
            response = openai.Completion.create(
                engine="text-davinci-003", prompt=prompt, max_tokens=5
            )
            # Parse OpenAI response to determine relevance
            result = response.choices[0].text.strip().lower()
            return "yes" in result
        except Exception as e:
            self.logger.error(f"OpenAI API request failed: {e}")
            return False
