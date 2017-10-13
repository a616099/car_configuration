# -*- coding: utf-8 -*-
import scrapy , datetime, re
from scrapy.selector import Selector
from ycconfig.items import YcconfigItem
from scrapy.shell import inspect_response   

class Ycconfig_Spider(scrapy.Spider):
    name = 'yiche'
    # test_url = 'http://car.bitauto.com/quanxinaodia4l/'

    def start_requests(self):
        url = 'http://car.bitauto.com/brandlist.html'

        yield scrapy.Request(url=url, callback=self.model_urls, dont_filter=True)

    # def start_requests(self):

    #     request = scrapy.Request(url=self.test_url, callback=self.car_urls, dont_filter=True)
    #    # request.meta['PhantomJS'] = True
    #     yield request

    def model_urls(self, response):
        for i in Selector(response).xpath("//div[@class='name']"):
            u = i.xpath("a/@href").extract_first()
            model_pinyin = u.strip('/')
            meta = {'model_pinyin':model_pinyin}
            yield scrapy.Request(url='http://car.bitauto.com%s'%u, 
                meta=meta,
                callback=self.car_urls, 
                dont_filter=True)

    def car_urls(self, response):
        sel = Selector(response)
        meta = response.meta
        meta['PhantomJS'] = True
        offsale = sel.xpath("//li[@class='offsale-years drop-layer-box']/div/a/@href").extract()
        years = [i.split('/')[-1] for i in offsale]
        url = ["%speizhi/%s/"%(response.url, i) for i in years]
        url.append(response.url+"peizhi/")

        for u in url:
            yield scrapy.Request(url=u, 
                meta=meta,
                callback=self.parse_item, 
                dont_filter=True)

    def chooseline(self, n, ind):
        l_n = ind.keys()

        for i,o in enumerate(l_n):
            if i+1 == len(l_n):
                return ind[list(l_n)[i]]
                pass
            if n in range(o+1,list(l_n)[i+1]):
                return ind[list(l_n)[i]]


    def parse_item(self, response):
        # inspect_response(response, self)
        item = YcconfigItem()
        sel = Selector(response)
        meta = response.meta
        ind = {}
        tr = sel.xpath("//div[@id='CarCompareContent']/table/tbody/tr")[1:]
        for i in tr:
            if i.xpath("td/h2/span"):
                k = tr.index(i)
                v = i.xpath("td/h2/span/text()").extract()[0]
                ind[k] = v

        for line in tr:
            if line.xpath('*')[0].xpath('string(.)').extract_first() == '燃油变速箱类型':
                paidang_line = line.xpath('*')[1:].xpath('string(.)').extract()

        model = re.search(r'var CarCommonCSID = \'(.*)\';', response.text).group(1)
        brand = sel.xpath("//h1/a/img/@alt").extract_first()
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

                    item['paidang'] = paidang_line[index]
                    item['version_id'] = version_id
                    item['version'] = version_name
                    item['classfy'] = title
                    item['item'] = th
                    item['karw']  = ll
                    item['url'] = url
                    item['model'] = model
                    item['brand'] = brand
                    now = datetime.datetime.now()
                    item['collect_date'] = now.strftime("%Y-%m-%d")
                    model_name = sel.xpath("//div[@class='brand-info']/h1/a/text()").extract()[0]
                    item['standard_version'] = '%s %s'%(model_name,version_name)
                    item['model_pinyin'] = meta['model_pinyin']

                    yield item
                    # print(item)