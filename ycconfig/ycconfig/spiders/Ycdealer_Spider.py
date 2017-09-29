# -*- coding: utf-8 -*-
import scrapy , datetime
from scrapy.selector import Selector
from ycconfig.items import DealerItem
from scrapy.shell import inspect_response

class DealerSpider(scrapy.Spider):
    name = 'yichedealer'
    base_url = 'http://dealer.bitauto.com'
    # test = 'http://dealer.bitauto.com/3802006/cars.html'

    def start_requests(self):
        url = 'http://dealer.bitauto.com/beijing'
        request = scrapy.Request(url=url, callback=self.brand_urls, dont_filter=True)
        request.meta['PhantomJS'] = True
        yield request

    # def start_requests(self):
    #     request = scrapy.Request(url=self.test, callback=self.parse, dont_filter=True)
    #     # request.meta['PhantomJS'] = True
    #     yield request

    def brand_urls(self, response):

        sel = Selector(response)
        left_list = sel.xpath("//ul[@class='list-con']/li/ul/li/a")
        for item in left_list:
            u = item.xpath("@href").extract_first()
            logo = item.xpath("div/span/text()").extract_first()
            meta = {'logo': logo}
            yield scrapy.Request(url='%s%s'%(self.base_url, u), meta=meta, callback=self.dealer_urls, dont_filter=True)

    def dealer_urls(self, response):

        sel = response
        meta = response.meta
        local_list = sel.xpath("//div[@id='d_pro']/div/ul/li/a")
        for i in local_list:
            u = i.xpath("@href").extract_first()
            lo = i.xpath("text()").extract_first()
            meta["localtion"] = lo
            yield scrapy.Request(url='%s%s'%(self.base_url, u), meta=meta, callback=self.all_dealer_urls, dont_filter=True)

    def all_dealer_urls(self, response):

        sel = response
        dealer_boxr = sel.xpath("//div[@class='main-inner-section sm dealer-box']")
        h_urls = dealer_boxr.xpath("div/div/h6/a/@href").extract()
        meta = response.meta
        for u in h_urls:
            dealer_id = u.split("/")[-2]
            meta['dealer_id'] = dealer_id
            url = "%s/%s/cars.html"%(self.base_url, dealer_id)
            yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)

        next_page = dealer_boxr.xpath("div[@class='pagination']/div/a[@class='next_on']/@href").extract_first()

        if next_page:
            url = "%s%s"%(self.base_url, next_page)
            yield scrapy.Request(url=url, meta=meta, callback=self.all_dealer_urls, dont_filter=True)

    def parse(self, response):

        # inspect_response(response, self)
        item = DealerItem()
        sel = response
        meta = response.meta
        info = sel.xpath("//div[@class='inheader']/div[@class='info']")
        item['name'] = info.xpath("h1/text()").extract_first()
        item['address'] = info.xpath("div[@class='adress']/@title").extract_first()
        car_list = sel.xpath("//div[@class='car_list_item  item_wauto']")
        for car in car_list:
            item['brand'] = car.xpath("div/h3/a/text()").extract_first()
            tr = car.xpath("div[@class='car_price']/table/tbody/tr")
            for i in tr:
                if i.xpath("th[@class='fw']") :
                    pass
                else:
                    item['version_name'] = i.xpath("td")[0].xpath("a/@title").extract_first()
                    url = i.xpath("td")[0].xpath("a/@href").extract_first()
                    item['url'] = '%s%s'%(self.base_url, url)
                    item['version_id'] = url.split('/')[-1].split('.html')[0]
                    item['msrp'] = i.xpath("td")[1].xpath("text()").extract_first().strip()
                    item['sale'] = i.xpath("td")[3].xpath("a/text()").extract_first().strip()

                    item['dealer_id'] = response.meta['dealer_id']
                    item['logo'] = response.meta['logo']
                    item['localtion'] = response.meta['localtion']

                    now = datetime.datetime.now()
                    item['collect_date'] = now.strftime("%Y-%m-%d")
                    
                    yield item

        if  sel.xpath("//div[@id='pager']/span[@class='nolink']").extract_first() == u'下一页':
            next_page = sel.xpath("//div[@id='pager']/a")[-1].xpath("@href").extract_first()
            url = "%s%s"%(self.base_url, next_page)

            yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)


