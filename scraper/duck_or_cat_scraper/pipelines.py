import hashlib

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.python import to_bytes


class DuckOrCatImagesPipeline(ImagesPipeline):
    """Downloads images into a per-label subfolder: <IMAGES_STORE>/<label>/<hash>.jpg"""

    def get_media_requests(self, item, info):
        for url in item.get("image_urls", []):
            yield scrapy.Request(url, meta={"label": item["label"]})

    def file_path(self, request, response=None, info=None, *, item=None):
        label = request.meta.get("label", "unknown")
        image_hash = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f"{label}/{image_hash}.jpg"
