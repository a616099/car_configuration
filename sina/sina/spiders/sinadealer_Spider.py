# -*- coding: utf-8 -*-
import scrapy, datetime, json, re, requests
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from sina.items import DealerItem

class sinadealer_Spider(scrapy.Spider):
    name = 'sina_dealer'
    test_url = 'http://db.auto.sina.com.cn/dealer/2016/'

    def get_brand(self):
        js_text = requests.get('http://db.auto.sina.com.cn/api/cms/car/getBrandList.json')
        js_load = json.loads(js_text.text)
        brand_dict = {}
        for k in js_load['data'].keys():
             for ite in js_load['data'][k]:
                brand_dict[ite['id']] = ite['zhName']

        return brand_dict

    def start_requests(self):
        url = "http://dealer.auto.sina.com.cn/beijing/list/"

        yield scrapy.Request(
            url=url,
            callback=self.city,
            dont_filter=True,
            )

    # def start_requests(self):

    #     yield scrapy.Request(
    #         url=self.test_url,
    #         callback=self.parse,
    #         dont_filter=True,
            # )

    def city(self, response):

        meta = {}
        brand_dict = self.get_brand()
        sel = Selector(response)
        city_url = sel.xpath("//div[@id='dealer_city_holder']/a/@href").extract()
        city_url.append(response.url)
        for u in city_url:
            for b_id in brand_dict.keys():
                meta['brand'] = brand_dict[b_id]
                url = "%sd-%s.html"%(u, b_id)

                yield scrapy.Request(
                        url=url,
                        callback=self.brand,
                        dont_filter=True,
                        meta=meta,
                        )


    def brand(self, response):
        sel = Selector(response)
        meta = response.meta
        if sel.xpath("//div[@class='dealer_content']"):
            meta['localtion'] = sel.xpath("//a[@id='dealer_city']/span/text()").extract()[0]
            dealer_list = sel.xpath("//div[@class='dealer_content']/div/a/@href").extract()
            for d_u in dealer_list:
                dealer_id = d_u.split('v-')[-1].strip('.html')
                url = "http://db.auto.sina.com.cn/dealer/%s"%dealer_id
                meta['dealer_id'] = dealer_id
                yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        dont_filter=True,
                        meta=meta,
                        )
 

            page_nav = sel.xpath("//div[@class='pagination clearfix']/a/@class").extract()
            if page_nav and page_nav[-1] == 'next':
                next_page = sel.xpath("//div[@class='pagination clearfix']/a/@href").extract()[-1]

                yield scrapy.Request(
                            url=next_page,
                            callback=self.brand,
                            dont_filter=True,
                            meta=meta,
                            )

    def parse(self, response):
        item = DealerItem()
        sel = Selector(response)
        meta = response.meta
        item['name'] = sel.xpath("//h1/text()").extract()[0]
        item['address'] = sel.xpath("//a[@class='big_map_cg']/text()").extract()[0]
        item['info'] = ''
        item['url'] = response.url
        item['dealer_id'] = meta['dealer_id']
        item['brand'] = meta['brand']
        item['localtion'] = meta['localtion']
        now = datetime.datetime.now()
        item['collect_date'] = now.strftime("%Y-%m-%d")

        for li in sel.xpath("//ul[@class='car_quote_list paging ']/li"):
            item['model'] = li.xpath("div/div/h3/a/text()").extract()[0]
            for dd in li.xpath("dl/dd"):
                item['version_name'] = dd.xpath("span/text()")[0].extract()
                item['msrp'] = dd.xpath("span/text()")[1].extract()
                item['sale'] = dd.xpath("span/text()")[2].extract()
                item['version_id'] = ''

                yield item