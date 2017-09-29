# -*- coding: utf-8 -*-
import scrapy, datetime, json, re
from scrapy.selector import Selector
import string
# 破解css文本替换的模块
from carconfig.anti_block import get_complete_text_autohome

from carconfig.items import CarconfigItem
from scrapy.shell import inspect_response                 


class carconfig_Spider(scrapy.Spider):
    name = 'autohome_config'
    test_url = 'http://car.autohome.com.cn/config/series/3104.html'

    def start_requests(self):
        for i in string.ascii_uppercase:
            url = 'http://www.autohome.com.cn/grade/carhtml/%s.html'%i
            yield scrapy.Request(url=url, callback=self.car_url, dont_filter=True)
        

        # request = scrapy.Request(url=self.test_url, callback=self.car_url, dont_filter=True)
        # request.meta['PhantomJS'] = True
        # yield request

    def car_url(self, response):
        if response.body:
            # inspect_response(response, self)
            sel = Selector(response)
            dl = sel.xpath("//dl")
            for d in dl:
                logo = d.xpath("dt/div/a/text()").extract_first() 
                meta = {'brand':logo}
                for li in d.xpath("dd/ul/li"):
                    models = li.xpath("@id").extract_first()
                    if models:
                        brand = li.xpath("h4/a/text()").extract_first()
                        meta['model'] = models[1:]

                        url = 'http://car.autohome.com.cn/config/series/%s.html'%models[1:]

                        request = scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)
                        # request.meta['PhantomJS'] = True
                        yield request


    def parse(self, response):
        item = CarconfigItem()
        meta = response.meta
        item['model'] = meta['model']
        item['brand'] = meta['brand']
        now = datetime.datetime.now()
        item['collect_date'] = now.strftime("%Y-%m-%d")
        text = get_complete_text_autohome(response.text)
        paramtypeitems_json = re.search(r'\"paramtypeitems\":(\[.*\])\}\};',text,re.X)
        configtypeitems_json = re.search(r'\"configtypeitems\":(\[.*\])\}\};',text,re.X)

        if paramtypeitems_json:
            paramtypeitems_ls = json.loads(paramtypeitems_json.group(1))
            name_list = paramtypeitems_ls[0]['paramitems'][0]['valueitems']
            for paramclassfy in paramtypeitems_ls:
                paramitems = paramclassfy['paramitems']
                for paramitem in paramitems:
                    
                    item['classfy'] = paramclassfy['name']
                    item['item'] = paramitem['name']

                    for ind, obj in enumerate(paramitem['valueitems']):
                        item['version'] =  name_list[ind]['value']
                        item['standard_version'] = name_list[ind]['value']
                        item['karw'] = obj['value']
                        item['version_id'] = obj["specid"]
                        item['url'] = r"http://car.autohome.com.cn/config/spec/%s.html" % obj["specid"]
                    
                        yield item

        if configtypeitems_json:
            configtypeitems_ls = json.loads(configtypeitems_json.group(1))
            for configclassfy in configtypeitems_ls:
                configitems = configclassfy['configitems']
                for configitem in configitems:
                    
                    item['classfy'] = configclassfy['name']
                    item['item'] = configitem['name']

                    for ind, obj in enumerate(configitem['valueitems']):
                        item['version'] =  name_list[ind]['value']
                        item['standard_version'] = name_list[ind]['value']
                        item['karw'] = obj['value']
                        item['version_id'] = obj["specid"]
                        item['url'] = r"http://car.autohome.com.cn/config/spec/%s.html" % obj["specid"]
                        yield item


    # def parse(self, response):
    #     text = get_complete_text_autohome(response.text)
    #     sel = Selector(text=text)
    #     item = CarconfigItem()
    #     td = sel.xpath("//div[@id='config_nav']/table/tbody/tr/td")
    #     if not td.extract_first():
    #         return 
    #     for ind, li in enumerate(td):
    #         version_name = li.xpath("div[@class='carbox']/div/a/text()").extract_first()
    #         if version_name:
    #             url = li.xpath("div[@class='carbox']/div/a/@href").extract_first()
    #             item['version_id'] = url.split('spec/')[-1].split('/#pvareaid')[0]
    #             table = sel.xpath("//div[@id='config_data']/table[@class='tbcs']/tbody")

    #             item['url'] = url
    #             item['version'] = version_name
    #             item['model'] = response.meta['model']
    #             item['brand'] = response.meta['brand']
    #             now = datetime.datetime.now()
    #             item['collect_date'] = now.strftime("%Y-%m-%d")
    #             for t_i, tab in enumerate(table):
    #                 if t_i == 0:
    #                     title = u'价格'
    #                     for con in tab.xpath("tr"):
    #                         th = con.xpath('th')[0].xpath('string(.)').extract_first()
    #                         ll = con.xpath("td")[ind].xpath('string(.)').extract_first()
                            
    #                         item['classfy'] = title
    #                         item['item'] = th
    #                         item['karw']  = ll

    #                         yield item
    #                 else:
    #                     title = tab.xpath("tr")[0].xpath("th/h3/span/text()").extract_first()
    #                     for con in tab.xpath("tr")[1:]:
    #                         th = con.xpath('th')[0].xpath('string(.)').extract_first()
    #                         if  'carcolor' == con.xpath("th/div/@class").extract_first():
    #                             color = con.xpath("td/div/ul/li/a/@title").extract()
    #                             ll = ' '.join(color)
    #                         else:
    #                             ll = con.xpath("td")[ind].xpath('string(.)').extract_first()

    #                         item['classfy'] = title
    #                         item['item'] = th
    #                         item['karw']  = ll

    #                         yield item