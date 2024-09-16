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

# import weave

load_dotenv()
# weave.init("crawler")


class SAPOTCSpider(scrapy.Spider):
    name = "sap_otc_spider"

    start_urls = [
        "https://community.sap.com/t5/enterprise-resource-planning-blogs-by-members/sap-order-to-cash-process-sd/ba-p/13551270",
        "https://techconcepthub.com/otc-process-in-sap/",
    ]

    # summary = ""
    processed = set()

    # @weave.op()
    def parse(self, response):

        # page_content = response.text
        page_content = response.body
        cleaned_page = self.extract_text(page_content)
        # file_name = response.url.split("/")[-2] + ".html"
        if (response.url in self.processed) or (response.meta.get("depth", 0) >= 5):
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
            # is_relevant = self.is_related_to_sap_otc(cleaned_page, self.summary)
            is_relevant = True

        if is_relevant:
            fileName = f"SAP_OTC/{response.url.split('/')[-2]}.json"
            file_data = {
                "metadata": metadata,
                "content": cleaned_page,
            }
            with open(fileName, "w") as json_file:
                json.dump(file_data, json_file, indent=4)

            # self.summary = self.get_summary(cleaned_page, self.summary)

            for next_page in response.css("a::attr(href)").getall():
                if next_page is not None:
                    yield response.follow(next_page, callback=self.parse)

    # def is_related_to_sap_otc(self, content, summary):

    #     prompt = f"""
    #     \n\nSummary:\n{summary}
    #     \n\nContent:\n{content}...
    #     """

    #     try:

    #         response = openai.chat.completions.create(
    #             model=llm,
    #             messages=[
    #                 {
    #                     "role": "system",
    #                     "content": "You will be given a summary related to SAP OTC and some content. Determine if the content is related to SAP OTC. Respond with 'Yes' or 'No'.",
    #                 },
    #                 {
    #                     "role": "user",
    #                     "content": prompt,
    #                 },
    #             ],
    #             max_tokens=1,
    #         )

    #         result = response.choices[0].message.content
    #         # print(result)
    #         return "yes" in result.lower()
    #     except Exception as e:
    #         logging.ERROR(f"OpenAI API request failed: {e}")
    #         return False

    # def get_summary(self, content, summary_so_far):

    #     try:
    #         messages = [
    #             {
    #                 "role": "system",
    #                 "content": "You are an AI assistant tasked with summarizing content related SAP OTC. You are given the summary so far, and the extra content to summarize."
    #                 "If the summary so far is empty, you will be given the content to summarize. Respond with the summary of the content."
    #                 "Only return summary and do not include the content in the response.",
    #             },
    #             {
    #                 "role": "user",
    #                 "content": """
    #                 Summary so far: {summary_so_far}\nn
    #                 Content to add to summary: {content}
    #                 Summary:
    #                 """,
    #             },
    #         ]
    #         response = openai.chat.completions.create(
    #             model=llm, messages=messages, max_tokens=400
    #         )
    #         # print("summary response", response.choices[0].message.content)
    #         result = response.choices[0].message.content
    #         print(summary_so_far)
    #         # print(content)
    #         print(result)
    #         return result
    #     except Exception as e:
    #         logging.ERROR(f"OpenAI API request failed for summary: {e}")
    #         return ""

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
