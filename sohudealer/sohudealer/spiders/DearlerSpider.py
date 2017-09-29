# -*- coding: utf-8 -*-
import scrapy , datetime
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from sohudealer.items import DealerItem
import json

class DealerSpider(scrapy.Spider):
    name = "sohuDealer"

    def start_requests(self):
        url = 'http://auto.sohu.com/dealer/static/provinceArr.js'

        yield scrapy.Request(url=url, callback=self.city_arr, dont_filter=True)

    def city_arr(self, response):
        # inspect_response(response, self)
        js_code = response.text.split('var provinceArr =')[1]
        js_load = json.loads(js_code)
        for obj in js_load:
            ci = obj['id']
            lo = obj['name']
            if ci == '990000':
                continue
            url = 'http://dealer.auto.sohu.com/map/?city=%s'%ci
            localtion = lo.split('-')[-1]
            meta = {'localtion':localtion}
            yield scrapy.Request(url=url, meta=meta, callback=self.dealer_list, dont_filter=True)
            # print(url)

    def dealer_list(self, response):
        meta = response.meta
        script_tag = response.xpath("//script")[5].xpath('text()').extract()[0]
        js_code = script_tag.split('var')[1].strip().strip('dealerList =').strip(';')
        js_load = json.loads(js_code)
        for dealer_id in js_load[0]:
            meta.update({'dealer_id':dealer_id['id']})
            url = 'http://dealer.auto.sohu.com/%s'%dealer_id['id']

            yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)

    def parse(self, response):
        meta = response.meta
        sel = Selector(response)
        meta['logo'] = sel.xpath("//ul[@class='group-list']/li/span[@class='color1']/text()").extract()[0].strip()      
        meta['name'] = sel.xpath("//h3[@class='group-title']/a/text()").extract()[0]     
        meta['url'] = response.url
        meta['address'] = sel.xpath("//ul[@class='group-list']/li[@class='address']/p/span/text()").extract()[0]
        meta['info'] = sel.xpath("//h1[@class='dealers-name']/@title").extract()[0]
        
        url = '%s/price'%response.url
        yield scrapy.Request(url=url, meta=meta, callback=self.parse_item, dont_filter=True)
        

    def parse_item(self, response):
        item = DealerItem()
        meta = response.meta
        sel = Selector(response)
        box = sel.xpath("//div[@class='box']")
        for tbody in box:
            item['brand'] = tbody.xpath("div/h4/text()").extract()[0].strip()
            for tr in tbody.xpath("table/tbody/tr"):
                item['version_name'] = tr.xpath("td")[0].xpath("a/text()").extract()[0].strip()
                item['msrp'] = tr.xpath("td")[1].xpath("span/text()").extract()[0].strip()
                item['sale'] = tr.xpath("td")[3].xpath("span/text()").extract()[0].strip()
                version_url = tr.xpath("td")[0].xpath("a/@href").extract()[0].strip()
                item['version_id'] = version_url.split('=')[-1]
                item['dealer_id'] = meta['dealer_id']
                item['localtion'] = meta['localtion']
                now = datetime.datetime.now()
                item['collect_date'] = now.strftime("%Y-%m-%d")
                item['logo'] = meta['logo']
                item['name'] = meta['name']
                item['url'] = meta['url']
                item['address'] = meta['address']
                item['info'] = meta['info']
                print(item['version_name'])
                print(item['name'])
                print(item['url'])                
                yield item