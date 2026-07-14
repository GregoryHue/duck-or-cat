import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "duck_or_cat_scraper"

SPIDER_MODULES = ["duck_or_cat_scraper.spiders"]
NEWSPIDER_MODULE = "duck_or_cat_scraper.spiders"

# Pexels is a sanctioned API accessed with our own key, not indiscriminate
# crawling, so robots.txt rules (meant for HTML crawlers) don't apply here.
ROBOTSTXT_OBEY = False

LOG_LEVEL = logging.DEBUG
LOG_FILE = "scrapy.log" 

CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.25

ITEM_PIPELINES = {
    "duck_or_cat_scraper.pipelines.DuckOrCatImagesPipeline": 1,
}

# Images are written to <IMAGES_STORE>/<label>/<hash>.jpg
IMAGES_STORE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
