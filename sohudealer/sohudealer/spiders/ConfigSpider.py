 # -*- coding: utf-8 -*-
import scrapy , datetime, json, requests, re
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from sohudealer.items import ConfigItem

class CongfigSpider(scrapy.Spider):
    name = 'sohu_config'

    # def start_requests(self):
    #     url = 'http://db.auto.sohu.com/yiqiaudi/2374/136970/trim.html'
    #     yield scrapy.Request(
    #         url=url, 
    #         callback=self.parse, 
    #         dont_filter=True
    #         )

    def start_requests(self):
        url = 'http://db.auto.sohu.com/home/'
        yield scrapy.Request(
            url=url, 
            callback=self.model_list, 
            dont_filter=True
            )

    def model_list(self, response):
        sel = Selector(response)
        brand_list = sel.xpath("//div[@class='tree_nav']/ul/li[@class='close_child']")
        for brand in brand_list:
            brand_name = ''.join(brand.xpath("h4/a/text()").extract()).strip()
            model_url = brand.xpath("ul/li/a[@class='model-a']/@href").extract()
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

    def chooseline(self, n, ind):
        l_n = ind.keys()
        for i,o in enumerate(l_n):
            if i+1 == len(l_n):
                return ind[list(l_n)[i]]
                pass
            if n in range(o+1,list(l_n)[i+1]):
                return ind[list(l_n)[i]]

    def parse(self, response):
        item = ConfigItem()
        sel = Selector(response)
        meta = response.meta
        json_url = 'http://db.auto.sohu.com/api/para/data/trim_%s.json'%meta['version_id']
        js_text = requests.get(json_url)
        js_code = js_text.text.replace('%u', r'\u').replace('%2e','.').replace('%2b','+')\
                .replace('%2d','-').replace('%2f','/').replace('%20',' ').replace('%28','(')\
                .replace('%29',')').replace('%26',')').replace('%7e','—')
        js_load = json.loads(js_code)
        color_291 = js_load['SIP_C_291']
        color_292 = js_load['SIP_C_292']
        js_load['SIP_C_291'] = ' '.join(re.findall(u"[\u4e00-\u9fa5]{1,10}\/[\u4e00-\u9fa5]{1,10}|[\u4e00-\u9fa5]{1,10}" , color_291))
        js_load['SIP_C_292'] = ' '.join(re.findall(u"[\u4e00-\u9fa5]{1,10}\/[\u4e00-\u9fa5]{1,10}|[\u4e00-\u9fa5]{1,10}" , color_292))

        ths_ids = response.xpath("//table[@id='trimArglist']/tbody/tr/@id").extract()
        idx = {}
        tr = response.xpath("//table[@id='trimArglist']/tbody/tr")
        for i in tr:
            if i.xpath("th/@class").extract_first() == 'colSpan6':
                k = tr.index(i)
                v = i.xpath("th/span[1]/text()").extract_first()
                idx[k] = v

        version_name = ' '.join(sel.xpath("//div[@class='top_tit']/a/text()").extract()).strip()
        for index, row in enumerate(tr):
            if index in idx:
                pass
            else:
                title = self.chooseline(index, idx)
                th = row.xpath('*')[0].xpath('string(.)').extract_first().strip()\
                                    .strip('：').strip().replace('\xa0','')
                row_id = row.xpath('@id').extract_first()
                ll = js_load.get(row_id,'-')

                item['paidang'] = js_load.get('SIP_C_158','')
                item['version_id'] = meta['version_id']
                item['version'] = version_name
                item['classfy'] = title
                item['item'] = th
                item['karw']  = ll
                item['url'] = response.url
                item['model'] = meta['model']
                item['brand'] = meta['brand']
                now = datetime.datetime.now()
                item['collect_date'] = now.strftime("%Y-%m-%d")
                item['standard_version'] = '%s %s'%(meta['brand'],version_name)

                # print(item)
                yield(item)