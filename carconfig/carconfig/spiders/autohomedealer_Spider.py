# -*- coding: utf-8 -*-
import scrapy , datetime
from scrapy.selector import Selector
from carconfig.items import DealerItem
from scrapy.shell import inspect_response

class DealerSpider(scrapy.Spider):
    name = 'autohomedealer'
    base_url = 'http://dealer.autohome.com.cn/'

    def start_requests(self):
        url = 'http://dealer.autohome.com.cn/china'
        request = scrapy.Request(url=url, callback=self.page_parse, dont_filter=True)
        request.meta['PhantomJS'] = True
        yield request

    def page_parse(self, response):

        sel = Selector(response)
        page_max = sel.xpath("//div[@id='pagination']/a/text()").extract()[-2]
        for numb in range(1,int(page_max)+1):
            url = "http://dealer.autohome.com.cn/china?countyId=0&brandId=0&seriesId=0&factoryId=0&pageIndex=%d&kindId=1&orderType=0&isSales=0&_abtest=1"%numb
    #     if sel.xpath("//div[@id='pagination']/span[@class='active disable']/text()").extract_first() != u'下一页':
    #         next_page = sel.xpath("//div[@id='pagination']/a/@href").extract()[-1]
    #         url = "%s%s"%(self.base_url, next_page)

            request = scrapy.Request(url=url, callback=self.url_list, dont_filter=True)
            request.meta['PhantomJS'] = True
            yield request

    def url_list(self, response): 
        sel = Selector(response)
        meta = {}
        dealer_list = sel.xpath("//div[@class='dealer-list-wrap']/ul/li")
        for dd in dealer_list:
            url = dd.xpath("ul/li")[1].xpath("a/@href").extract_first().strip('//')
            meta['dealer_id'] = url.split('/')[1]
            meta['name'] = dd.xpath("ul/li[@class='tit-row']/a/span/text()").extract_first()
            meta['logo'] = dd.xpath("ul/li")[1].xpath("span/em/text()").extract_first()
            meta['address'] = dd.xpath("ul/li")[3].xpath("span[@class='info-addr']/text()").extract_first()
            meta['url'] = url

            info_url = "%s%s/info.html"%(self.base_url, meta['dealer_id'])
            yield scrapy.Request(url=info_url, meta=meta, callback=self.dealer_info, dont_filter=True)


    def dealer_info(self, response):
        sel = Selector(response)
        info = sel.xpath("//div[@class='company-cont']")[0].xpath('string(.)').extract_first().strip()
        meta = response.meta
        meta['info'] = ''.join(info.split())[:100]
        url = "http://%s"%meta['url']

        yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)

    def parse(self, response):

        sel = Selector(response)
        item = DealerItem()
        meta = response.meta
        item['localtion'] = sel.xpath("//div[@id='breadnav']/a/text()").extract()[1]
        dl = sel.xpath("//dl[@class='price-dl']")
        for oj in dl:
            item['brand'] = oj.xpath("dt/div/p[@class='name-text font-yh']/a/text()").extract_first()
            tr = oj.xpath("dd/table/tr")
            for td in tr:
                if not td.xpath("th[@class='name txt-left']"):
                    item['version_name'] = td.xpath("td")[0].xpath("a/text()").extract_first()
                    version_href = td.xpath("td")[0].xpath("a/@href").extract_first()
                    item['version_id'] = version_href.split('spec_')[1].split('.html')[0]
                    item['msrp'] = td.xpath("td")[1].xpath("p/text()").extract_first()
                    item['sale'] = td.xpath("td")[2].xpath("div/a[@class='font-bold font-arial']/text()").extract_first() \
                                or td.xpath("td")[2].xpath("p/a/text()").extract_first()

                    item['dealer_id'] = meta['dealer_id']
                    item['name'] = meta['name']
                    item['logo'] = meta['logo']
                    item['address'] = meta['address']
                    item['url'] = meta['url']
                    item['info'] = meta['info']
                    
                    now = datetime.datetime.now()
                    item['collect_date'] = now.strftime("%Y-%m-%d")

                    yield item
