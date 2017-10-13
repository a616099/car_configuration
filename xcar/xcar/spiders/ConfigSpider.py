 # -*- coding: utf-8 -*-
import scrapy , datetime, json, requests, re
from scrapy.selector import Selector
from scrapy.shell import inspect_response

class CongfigSpider(scrapy.Spider):
    name = 'xcar_config'

    def start_requests(self):
        model_list = response.xpath("//div[@id='img_load_box']/div/table/tbody/tr")
        for item in model_list:
            brand = item.xpath("td/div/a/img/@title").extract_first()
            model = item.xpath("td/div/ul/li/div/a/@href").extract()
            