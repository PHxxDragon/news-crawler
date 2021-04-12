# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    dateAndTime = scrapy.Field()
    tags = scrapy.Field()
    bodyText = scrapy.Field()
    comments = scrapy.Field()
