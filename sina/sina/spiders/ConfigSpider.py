 # -*- coding: utf-8 -*-
import scrapy , datetime, json, requests, re
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from sina.items import SinaItem

class CongfigSpider(scrapy.Spider):
    name = 'sina_config'

    def start_requests(self):
        url = 'http://db.auto.sina.com.cn'
        yield scrapy.Request(
            url=url,
            callback=self.model_list,
            dont_filter=True,
            )

    def model_list(self, response):
        sel = Selector(response)
        for u in sel.xpath("//a[@data-type='subid']/@href").extract():
            url = 'http:%s'%u
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                dont_filter=True,
                )

    def parse(self, response):
        sel = Selector(response)
        item = SinaItem()
        brand = sel.xpath("//a[@class='fL logo']/img/@alt").extract_first()
        model = response.url.strip('/').split('/')[-1]
        model_name = sel.xpath("//span[@class='fL name']/a[1]/text()").extract_first()

        js_pi_url = 'http://db.auto.sina.com.cn/api/car/getFilterCar.json?subid=%s&niankuan=&derailleur_type=&product_status=1,2&outgas=&auto_type='%model
        js_p_text = requests.get(js_pi_url)
        js_p_load = json.loads(js_p_text.text)
        tds = sel.xpath("//div[@class='cartype_list lump']/table/tbody/tr/td[1]")
        for td in tds:
            url = td.xpath('a[1]/@href').extract_first()
            version_name = td.xpath('a[1]/span/text()').extract_first()
            version_id = url.strip('/').split('/')[-1]

            js_url = 'http://db.auto.sina.com.cn/api/car/getFilterCarInfo.json?carid=%s'%version_id
            js_text = requests.get(js_url)
            js_load = json.loads(js_text.text)

            for i in js_load['baseinfo']['data']:
                if i['name'] == '变速箱':
                    paidang = i['data'][-1].get('data','')

            item['paidang'] = paidang
            item['version_id'] = version_id
            item['version'] = version_name
            item['url'] = response.url
            item['model'] = model
            item['brand'] = brand
            now = datetime.datetime.now()
            item['collect_date'] = now.strftime("%Y-%m-%d")
            item['standard_version'] = '%s %s'%(model_name,version_name)

            for i in js_p_load:
                if i['car_id'] == version_id:
                    item['classfy'] = '厂商指导价'
                    item['item'] = '厂商指导价'
                    item['karw'] = i['merchant_price_indoor']
                    
                    yield(item)

            for k in js_load.keys():
                for data in js_load[k].get('data',''):
                    item['classfy'] = js_load[k]['name']
                    item['item'] = data['name']
                    item['karw']  = data['data'][-1].get('data','')

                    # print(item)
                    yield(item)