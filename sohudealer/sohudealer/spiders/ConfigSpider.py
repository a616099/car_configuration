 # -*- coding: utf-8 -*-
import scrapy , datetime, json, requests, re
from scrapy.selector import Selector
from scrapy.shell import inspect_response

class CongfigSpider(scrapy.Spider):
    name = 'sohu_config'

    def start_requests(self):
        url = 'http://db.auto.sohu.com/yiqiaudi/2374/136970/trim.html'
        yield scrapy.Request(
            url=url, 
            callback=self.parse, 
            dont_filter=True
            )

    # def start_requests(self):
    #     url = 'http://db.auto.sohu.com/home/'
    #     yield scrapy.Request(
    #         url=url, 
    #         callback=self.model_list, 
    #         dont_filter=True
    #         )

    def model_list(self, response):
        sel = Selector(response)
        brand_list = sel.xpath("//div[@class='tree_nav']/ul/li[@class='close_child']")
        for brand in brand_list:
            brand_name = ''.join(i.xpath("h4/a/text()").extract()).strip()
            model_url = i.xpath("ul/li/a[@class='model-a']/@href").extract()
            for u in model_url:
                meta = {
                    'model':u.split('/')[-1], 
                    'brand':brand_name,
                    }
                url = 'http:%s'%u
                yield scrapy.Request(
                    url=url,
                    meta=meta,
                    callback=self.car,
                    dont_filter=True,
                    )

    def car(self, response):
        sel = Selector(response)
        meta = response.meta    
        url = sel.xpath("//td[@class='ftdleft']/a[@uigs='cklb']/@href").extract()
        version_ids = [i.split('/')[-1].split('?')[0] for i in url]
        for version_id in version_ids:
            meta['version_id'] = version_id
            url = "%s/%s/trim.html"%(response.url, version_id)
            yield scrapy.Request(
                url=url,
                meta=meta,
                callback=self.parse,
                dont_filter=True,
                )

    def parse(self, response):
        sel = Selector(response)
        meta = response.meta
        json_url = 'http://db.auto.sohu.com/api/para/data/trim_%s.json'%meta['version_id']
        js_text = requests.get(json_url)
        js_code = js_text.text.replace('%u', r'\u').replace('%2e','.').replace('%2b','+').replace('%2d','-').replace('%2f','/').replace('%20',' ')
        js_load = json.loads(js_code)
        color_291 = js_load['SIP_C_291']
        color_292 = js_load['SIP_C_292']
        js_load['SIP_C_291'] = re.findall(u"[\u4e00-\u9fa5]{10}" , color_291)
        js_load['SIP_C_292'] = re.findall(u"[\u4e00-\u9fa5]{10}" , color_292)

        ths_ids = response.xpath("//table[@id='trimArglist']/tbody/tr/@id").extract()
