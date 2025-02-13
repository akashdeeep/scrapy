#!/bin/bash

# Default values
DEFAULT_START_URLS="https://businessprocessxperts.com/order-to-cash-o2c-solutions-sap-expert/"
DEFAULT_DEPTH=3

# Accept custom start_urls and depth from command line if provided
START_URLS=${1:-$DEFAULT_START_URLS}
DEPTH=${2:-$DEFAULT_DEPTH}

# Running the Scrapy spider with the provided or default arguments
scrapy runspider SAP1/spiders/sap_otc_spider.py -a start_urls="$START_URLS" -a depth="$DEPTH" -s LOG_FILE=SAP1/logs/otc_spider.log
