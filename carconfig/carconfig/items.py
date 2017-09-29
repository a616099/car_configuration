# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 车型配置表
class CarconfigItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    brand = scrapy.Field()
    # 车型
    model = scrapy.Field()

    # 型号
    version = scrapy.Field()

    version_id = scrapy.Field()

    url = scrapy.Field()
    #配置
    classfy = scrapy.Field()

    item = scrapy.Field()

    karw = scrapy.Field()
    
    collect_date = scrapy.Field() 
    
    standard_version = scrapy.Field()


# 经销商
class DealerItem(scrapy.Item):
    dealer_id = scrapy.Field()
    logo = scrapy.Field()
    brand = scrapy.Field()
    name = scrapy.Field()
    localtion = scrapy.Field()
    url = scrapy.Field()
    collect_date = scrapy.Field()
    address = scrapy.Field()
    msrp = scrapy.Field()
    sale = scrapy.Field()
    version_id = scrapy.Field()
    version_name = scrapy.Field()
    info = scrapy.Field()


