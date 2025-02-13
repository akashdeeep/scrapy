#!/bin/bash

# Default values
DEFAULT_URL_FILE="start_urls.txt"
DEFAULT_DEPTH=3

# Accept custom URL file and depth from command line if provided
URL_FILE=${1:-$DEFAULT_URL_FILE}
DEPTH=${2:-$DEFAULT_DEPTH}

# Check if the file exists
if [[ ! -f "$URL_FILE" ]]; then
    echo "Error: URL file '$URL_FILE' not found!"
    exit 1
fi

# Read URLs from the file and join them with a comma
START_URLS=$(tr '\n' ',' < "$URL_FILE" | sed 's/,$//')

# Run the Scrapy spider with the extracted URLs
scrapy runspider SAP1/spiders/sap_otc_spider.py -a start_urls="$START_URLS" -a depth="$DEPTH" -s LOG_FILE=SAP1/logs/otc_spider.log
