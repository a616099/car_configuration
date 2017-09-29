# -*- coding: utf-8 -*-
import scrapy , datetime
from scrapy.selector import Selector
from ycconfig.items import YcconfigItem
from scrapy.shell import inspect_response   

class Ycconfig_Spider(scrapy.Spider):
    name = 'yiche'
    # test_url = 'http://car.bitauto.com/kaiyic3r/peizhi/'

    def start_requests(self):
        url = 'http://car.bitauto.com/tree_chexing/'

        request = scrapy.Request(url=url, callback=self.brand_urls, dont_filter=True)
        request.meta['PhantomJS'] = True
        yield request

    # def start_requests(self):

    #     request = scrapy.Request(url=self.test_url, callback=self.parse_item, dont_filter=True)
    #     request.meta['PhantomJS'] = True
    #     yield request

    def brand_urls(self, response):
        sel = Selector(response)
        brand_urls = sel.xpath("//ul[@class='list-con']/li/ul/li/a/@href").extract()
        for u in brand_urls:
            yield scrapy.Request(url='http://car.bitauto.com%s'%u, callback=self.car_urls, dont_filter=True)

    def car_urls(self, response):

        sel = Selector(response)
        car_urls = sel.xpath("//div[@id='divCsLevel_0']/div/div/div/div/a/@href").extract()
        brand = sel.xpath("//div[@class='section-header header1 h-default']/div/h2/a/text()").extract_first()
        meta = {'brand': brand}
        for u in car_urls:
            meta['model'] = u.strip('/')
            meta['PhantomJS'] = True
            url = 'http://car.bitauto.com%speizhi/'%u
            request = scrapy.Request(url=url, callback=self.parse_item, meta=meta, dont_filter=True)

            yield request

    def chooseline(self, n, ind):
        l_n = ind.keys()

        for i,o in enumerate(l_n):
            if i+1 == len(l_n):
                return ind[list(l_n)[i]]
                pass
            if n in range(o+1,list(l_n)[i+1]):
                return ind[list(l_n)[i]]


    def parse_item(self, response):

        item = YcconfigItem()
        sel = Selector(response)

        ind = {}
        tr = sel.xpath("//div[@id='CarCompareContent']/table/tbody/tr")[1:]
        for i in tr:
            # if len(i.xpath("*").extract()) == 1:
            if i.xpath("td/h2/span"):
                k = tr.index(i)
                v = i.xpath("td/h2/span/text()").extract()[0]
                ind[k] = v

        version_url = sel.xpath("//div[@id='CarCompareContent']/table/tbody/tr/td[@class='pd0']").extract()
        for index,row in enumerate(sel.xpath("//div[@id='CarCompareContent']/table/tbody/tr/td[@class='pd0']//dl")):
            version_name = row.xpath('dd/a/text()').extract_first()
            url = 'http://car.bitauto.com%speizhi/'%(row.xpath('dd/a/@href').extract_first())
            version_id = row.xpath('dd/a/@href').extract_first().split('/')[-2][1:]

            for n,line in enumerate(tr):
                if n in ind:
                    pass

                else:
                    title = self.chooseline(n ,ind) 

                    ll = line.xpath('*')[index+1].xpath('string(.)').extract_first().replace(u'\xa0', ' ')
                    th = line.xpath('*')[0].xpath('string(.)').extract_first().replace(u'\xa0', ' ') 
                    if line.xpath("@id").extract_first() == 'tr1_1':
                        ll = line.xpath("*")[index+1].xpath("div/span/a/text()").extract_first() or \
                             line.xpath("*")[index+1].xpath("string(.)").extract_first()
                    if line.xpath("@class").extract_first() == 'p-color h60':
                        color = line.xpath("*")[index+1].xpath("ul/li/a/@title").extract()
                        ll = ' '.join(color)

                    item['version_id'] = version_id
                    item['version'] = version_name
                    item['classfy'] = title
                    item['item'] = th
                    item['karw']  = ll
                    item['url'] = url
                    item['model'] = response.meta['model']
                    item['brand'] = response.meta['brand']
                    now = datetime.datetime.now()
                    item['collect_date'] = now.strftime("%Y-%m-%d")
                    model_name = sel.xpath("//div[@class='brand-info']/h1/a/text()").extract()[0]
                    item['standard_version'] = '%s %s'%(model_name,version_name)

                    yield item
                    # print(item)