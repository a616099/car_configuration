# -*- coding: utf-8 -*-
import scrapy , datetime
from scrapy.selector import Selector
from scrapy.shell import inspect_response
import json
from auto163.items import DealerItem

class DealerSpider(scrapy.Spider):
    name = "auto163Dealer"

    def start_requests(self):
        url = "http://product.auto.163.com/dealer/gfcitys.js"
        meta={'PhantomJS':False}
        yield scrapy.Request(url=url, meta=meta, callback=self.city_arr, dont_filter=True)

    # def start_requests(self):
    #     url = "http://dealers.auto.163.com/36546/price.html"
    #     meta={'PhantomJS':False}
    #     yield scrapy.Request(url=url, meta=meta, callback=self.parse_items, dont_filter=True)

    def city_arr(self, response):
        body = response.body.decode('gbk')
        js_code = body.lstrip('var data_city=').rstrip(';')
        js_load = json.loads(js_code, encoding="utf-8")
        meta={'PhantomJS':True}
        for mm in js_load:
            if mm['parentid'] != '0':
                city_id = mm['id']
                city = mm['name']
                url = 'http://dealers.auto.163.com/search/%s/'%city_id
                meta['city_id'] = mm['id']
                meta['localtion'] = mm['name']
                yield scrapy.Request(url=url, meta=meta, callback=self.dealer_list, dont_filter=True)

    def dealer_list(self, response):
        sel = Selector(response)
        meta = response.meta
        meta['PhantomJS'] = False
        city_id = meta['city_id']
        # city_id = '445100'
        ss = "http://dealers.auto.163.com/search/api/dealers/"
        page_nav = sel.xpath("//div[@class='pagination light-theme simple-pagination']/ul/li/a/text()").extract()
        if page_nav:
            max_page = page_nav[-2]
            for page in range(1, int(max_page)+1):
                url = "%s%s/all/%s_10.html"%(ss, city_id, str(page))
                yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)
        else:
            url = "%s%s/all/1_10.html"%(ss, city_id)
            yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)

    def parse(self, response):
        meta = response.meta
        js_load = json.loads(response.body)
        dealer_list = js_load['list']
        for dealer in dealer_list:
            try:
                website = dealer['website']
                dealer_id = website.split('/')[-2]
                meta['dealer_id'] = dealer_id
                meta['logo'] = ' '.join([i['name'] for i in dealer['main_brand']])
                meta['address'] = dealer['address']
            except:
                pass
            yield scrapy.Request(url=website+"price.html", meta=meta, callback=self.parse_items, dont_filter=True)

    def parse_items(self, response):
        item = DealerItem()
        sel = Selector(response)
        meta = response.meta
        item['name'] = sel.xpath("//div[@class='ds_name']/h2/text()").extract()[0]
        item['info'] = sel.xpath("//div[@class='ds_name']/h2/text()").extract()[0]
        car_list = sel.xpath("//div[@class='ds_hotcars']/div")[1:]
        for mo in car_list:
            item['brand'] = mo.xpath("div[@class='ds_topcar']/a/@title").extract()[0]
            tr = mo.xpath("div[@class='ds_car_other_cnt']/table/tr")
            for td in tr:
                item['version_name'] = td.xpath("td")[0].xpath("span/a/@title").extract()[0]
                v_url = td.xpath("td")[0].xpath("spa n/a/@href").extract()[0]
                item['version_id'] = v_url.split('/')[-1].strip('.html')
                item['url'] = response.url
                item['msrp'] = td.xpath("td")[1].xpath("span/text()").extract()[0]
                item['sale'] = td.xpath("td")[2].xpath("span/text()").extract()[0]

                item['localtion'] = meta['localtion']
                item['dealer_id'] = meta['dealer_id']
                item['logo'] = meta['logo']
                item['address'] = meta['address']

                now = datetime.datetime.now()
                item['collect_date'] = now.strftime("%Y-%m-%d")

                print(item['version_name'])
                print(item['name'])
                print(item['url'])         
                yield item