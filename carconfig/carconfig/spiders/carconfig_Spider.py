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
        

        # yield scrapy.Request(url=self.test_url, callback=self.parse, dont_filter=True)

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
                        sale_url = 'http://www.autohome.com.cn/%s/sale.html'%models[1:]

                        yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)
                        yield scrapy.Request(url=sale_url, meta=meta, callback=self.all_model, dont_filter=True)

    def all_model(self, response):
        meta = response.meta
        for i in response.xpath("//div[@class='models_nav']"):
            url = 'http://www.autohome.com.cn/%s'%i.xpath("a/@href")[1].extract()
            yield scrapy.Request(url=url, meta=meta, callback=self.parse, dont_filter=True)

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
            for i in paramtypeitems_ls:
              for p in i['paramitems']:
                if p['name'] == '变速箱类型':
                  paidang = p['valueitems']
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
                        item['paidang'] = paidang[ind]['value']

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
                        item['paidang'] = paidang[ind]['value']

                        yield item
