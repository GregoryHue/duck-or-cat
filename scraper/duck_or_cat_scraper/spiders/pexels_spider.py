import json

import scrapy

from duck_or_cat_scraper.items import DuckOrCatItem

API_URL = "https://api.pexels.com/v1/search"


class PexelsSpider(scrapy.Spider):
    """Fetches duck/cat photos from the Pexels API.

    Usage:
        scrapy crawl pexels -a labels=cat,duck -a images_per_label=500
    """

    name = "pexels"
    # No allowed_domains: the API lives on api.pexels.com but actual image
    # files are served from images.pexels.com (and possibly other Pexels
    # CDN hosts), which OffsiteMiddleware would otherwise silently block.

    def __init__(self, labels="cat,duck", images_per_label=500, per_page=80, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.labels = [label.strip() for label in labels.split(",") if label.strip()]
        self.images_per_label = int(images_per_label)
        self.per_page = min(int(per_page), 80)  # Pexels caps per_page at 80

    async def start(self):
        api_key = self.settings.get("PEXELS_API_KEY")
        if not api_key:
            raise ValueError(
                "PEXELS_API_KEY is not set. Copy .env.example to .env and add your key."
            )
        headers = {"Authorization": api_key}
        for label in self.labels:
            url = f"{API_URL}?query={label}&per_page={self.per_page}&page=1"
            yield scrapy.Request(
                url,
                headers=headers,
                callback=self.parse,
                meta={"label": label, "page": 1, "fetched": 0},
            )

    def parse(self, response):
        label = response.meta["label"]
        page = response.meta["page"]
        fetched = response.meta["fetched"]

        data = json.loads(response.text)
        photos = data.get("photos", [])

        for photo in photos:
            if fetched >= self.images_per_label:
                break
            image_url = photo["src"]["large2x"]
            yield DuckOrCatItem(
                image_urls=[image_url],
                label=label,
                source_id=str(photo["id"]),
            )
            fetched += 1

        # Pexels' own `next_page` field is malformed (it duplicates the /v1/
        # path segment, e.g. https://api.pexels.com/v1/v1/search?...), which
        # 404s every time. Build the next page URL ourselves instead of
        # trusting it, and use the page being full as the "more pages" signal.
        has_more_pages = len(photos) == self.per_page
        if has_more_pages and fetched < self.images_per_label:
            next_url = f"{API_URL}?query={label}&per_page={self.per_page}&page={page + 1}"
            yield scrapy.Request(
                next_url,
                headers=response.request.headers,
                callback=self.parse,
                meta={"label": label, "page": page + 1, "fetched": fetched},
            )
