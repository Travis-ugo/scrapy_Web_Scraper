# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PoizonscraperItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    pass


class ProductItems(scrapy.Item):
    Name = scrapy.Field()
    Categories = scrapy.Field()
    Color = scrapy.Field()
    Images = scrapy.Field()
    Link = scrapy.Field()
    SpuId = scrapy.Field()
    CategoryId = scrapy.Field()
    Brand = scrapy.Field()
    Vendor = scrapy.Field()


