# -*- coding: utf-8 -*-
import scrapy, datetime, json, re
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from xcar.items import DealerItem

class xcardealer_Spider(scrapy.Spider):
    name = 'xcar_dealer'
    test_url = "http://dealer.xcar.com.cn/91715/price_1_1.htm"
    
    def start_requests(self):
        url = 'http://dealer.xcar.com.cn/'

        yield scrapy.Request(
                url=url,
                callback=self.get_province,
                dont_filter=True,
                )

    # def start_requests(self):
    #     yield scrapy.Request(
    #             url=self.test_url,
    #             callback=self.parse,
    #             dont_filter=True,
    #             # meta={'PhantomJS':True},
    #             )

    def get_province(self, response):
        sel = Selector(response)
        province_id = sel.xpath("//ul[@id='select_province']/li/@value").extract()
        province_id.remove('1000')
        province_id.remove('0')
        for pro_id in province_id:
            url = "http://dealer.xcar.com.cn/dealerdp_index.php?r=dealers/Ajax/selectCity&province_id=%s&pbid=0"%pro_id
            yield scrapy.Request(
                url=url,
                callback=self.get_city,
                dont_filter=True,
                  )

    def get_city(self, response):
        sel = Selector(response)
        for city_s in sel.xpath("//li")[1:]:
            city_id = city_s.xpath("@id").extract()[0]
            city = city_s.xpath("@name").extract()[0]
            meta = {'city':city}
            url = "http://dealer.xcar.com.cn/%s/"%city_id
            yield scrapy.Request(
                url=url,
                callback=self.dealer_list,
                dont_filter=True,
                meta=meta,
                  )
            
    def dealer_list(self, response):
        meta = response.meta
        sel = Selector(response)
        for dealer in sel.xpath("//ul[@class='dlists_list']/li"):
            dealer_id = dealer.xpath("dl/dt/a")[0].xpath("@href").extract()[0].strip('/')
            url = "http://dealer.xcar.com.cn/%s/price_1_1.htm"%dealer_id
            meta['dealer_id'] = dealer_id
            meta['address'] = dealer.xpath("dl/dd[@class='site']/span/@title").extract()[0]
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                dont_filter=True,
                meta=meta
                  )    

        page_nav = sel.xpath("//div[@class='unify_page']/a/@class").extract()
        if page_nav:
            if page_nav[-1] != 'page_down_no':
                url = sel.xpath("//div[@class='unify_page']/a/@href").extract()[-1]
                yield scrapy.Request(
                    url="http://dealer.xcar.com.cn%s"%url,
                    callback=self.dealer_list,
                    dont_filter=True,
                    meta=meta,
                      )
    #         print(url)

    def parse(self, response):
        sel = Selector(response)
        item = DealerItem()
        # inspect_response(response, self)
        meta = response.meta
        item['localtion'] = meta['city']
        item['dealer_id'] = meta['dealer_id']
        item['address'] = meta['address']
        now = datetime.datetime.now()
        item['collect_date'] = now.strftime("%Y-%m-%d")
        item['name'] = sel.xpath("//dl[@class='clearfix']/dd/span/text()").extract()[0]
        item['info'] = sel.xpath("//dl[@class='clearfix']/dd/span/text()").extract()[0]
        logo_list = sel.xpath("//dl[@class='pp_list clearfix']/dd/span/text()").extract()
        item['brand'] = ' '.join(logo_list)
        for car_list in sel.xpath("//div[@class='car_xin_z']/div"):
            item['model'] = car_list.xpath("div[@class='car_t']/dl/dd/div/span[@class='nama_lf']/text()").extract()[0]
            tbody = car_list.xpath("div[@class='price_list']/table/tbody")
            for trs in tbody:
                for td in trs.xpath("tr")[1:]:
                    item['version_name'] = td.xpath("td")[0].xpath("a/text()").extract()[0]
                    item['version_id'] = td.xpath("td")[0].xpath("a/@href").extract()[0].split('_')[-1].strip('.htm')
                    item['msrp'] = td.xpath("td")[1].xpath("text()").extract()[0]
                    item['sale'] = td.xpath("td")[3].xpath("i/text()").extract()[0]

                    item['url'] = response.url

                    yield item

        page_nav = sel.xpath("//div[@class='unify_page']/a/@class").extract()
        if page_nav:
            if page_nav[-1] != 'page_down_no':
                url = sel.xpath("//div[@class='unify_page']/a/@href").extract()[-1]
                yield scrapy.Request(
                    url="http://dealer.xcar.com.cn%s"%url,
                    callback=self.parse,
                    dont_filter=True,
                    meta=meta,
                      )