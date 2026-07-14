import scrapy


class DuckOrCatItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    label = scrapy.Field()
    source_id = scrapy.Field()
