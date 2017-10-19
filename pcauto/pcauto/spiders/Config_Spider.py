 # -*- coding: utf-8 -*-
import scrapy , datetime, json, requests, re
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from pcauto.items import PcautoItem

class Config_Spider(scrapy.Spider):
    name = 'pcauto_config'
    # test_url = "http://price.pcauto.com.cn/sg7641/config.html"

    def start_requests(self):
        url = "http://price.pcauto.com.cn/api/hcs/select/compareNewBar/serial_brand_json_chooser?type=1"
        yield scrapy.Request(
            url=url, 
            callback=self.model_list, 
            dont_filter=True
            )
    # def start_requests(self):
    #     yield scrapy.Request(
    #         url=self.test_url, 
    #         callback=self.parse, 
    #         dont_filter=True
    #         )

    def model_list(self, response):
        meta = {}
        body = response.body.decode('gbk')
        text = body.replace(r'\n','').replace(r'\r','')
        js_text = text.strip().lstrip('var listCompareInfo = ').rstrip(';')
        js_load = json.loads(js_text)
        for mm in js_load:
            meta['brand'] = mm['NAME']
            for cj in mm['LIST']:
                for car in cj['LIST']:
                    meta['model'] = car['ID']
                    meta['model_name'] = car['NAME']

                    url = 'http://price.pcauto.com.cn/sg%s/config.html'%car['ID']
                    yield scrapy.Request(
                        url=url, 
                        callback=self.all_sale, 
                        dont_filter=True,
                        meta=meta,
                        )

    def all_sale(self, response):
        offsale = response.xpath("//div[@class='stopDrop']/a/@href").extract()
        url = ["http://price.pcauto.com.cn%s"%i for i in offsale]
        url.append(response.url)
        meta = response.meta
        
        for u in url:
            yield scrapy.Request(
                url=u, 
                callback=self.parse, 
                dont_filter=True,
                meta=meta,
                )
        
#http://price.pcauto.com.cn/sg7641/config.html
    def parse(self, response):
        item = PcautoItem()
        body = response.body.decode('gbk')
        text = body.replace(r'\n','').replace(r'\r','')
        meta = response.meta
        item['brand'] = meta['brand']
        item['model'] = meta['model']
        params, equ_ = text.split('//params')[-1].split('//equips')
        equips, col_ = equ_.split('//colors')
        colors, innercol_ = col_.split('//车型内饰colors')
        innercolors = innercol_.split('//经销商报价')[0]
        js_params_text = re.search(r'var config = (\{.*\});', params).group(1)
        js_equips_text = re.search(r'var option = (\{.*\});', equips).group(1)
        js_colors_text = re.search(r'var color = (\{.*\});', colors).group(1)
        js_innercolors_text = re.search(r'var innerColor = (\{.*\});', innercolors).group(1)
        now = datetime.datetime.now()

        if js_params_text:
            js_params_code = json.loads(js_params_text.replace("curId", "\"curId\""))
            for vers in js_params_code['body']['items']:
                if vers['Name'] == '变速箱类型':
                    paidang = vers['ModelExcessIds']  
                else:
                    paidang = ''        
            version_cow = js_params_code['body']['items'][0]['ModelExcessIds']
            for vers in js_params_code['body']['items']:
                for ind,v in enumerate(vers['ModelExcessIds']):
                    item['classfy'] = vers['Item']
                    item['item'] = vers['Name']
                    item['karw'] =  v['Value']
                    item['version_id'] = v['Id']
                    item['version'] = version_cow[ind]['Value']
                    item['standard_version'] = version_cow[ind]['Value']
                    item['url'] = "http://price.pcauto.com.cn/m%s/config.html"%v['Id']
                    item['collect_date'] = now.strftime("%Y-%m-%d")
                    if paidang:
                        item['paidang'] = paidang[ind]['Value']
                    else:
                        item['paidang'] = paidang
                        
                    yield item
                    # print(item)

        if js_equips_text:
            js_equips_code = json.loads(js_equips_text)
            for vers in js_equips_code['body']['items']:
                for ind,v in enumerate(vers['ModelExcessIds']):
                    item['classfy'] =  vers['Item']
                    item['item'] = vers['Name']
                    item['karw'] = v['Price']
                    item['version_id'] = v['Id']
                    item['version'] = version_cow[ind]['Value']
                    item['standard_version'] = version_cow[ind]['Value']
                    item['url'] = "http://price.pcauto.com.cn/m%s/config.html"%v['Id']
                    item['collect_date'] = now.strftime("%Y-%m-%d")
                    if paidang:
                        item['paidang'] = paidang[ind]['Value']
                    else:
                        item['paidang'] = paidang
                    yield item
                    # print(item)

        if js_colors_text:
            js_colors_code = json.loads(js_colors_text)
            for ind, vers in enumerate(js_colors_code['body']['items']):
                item['classfy'] = '驾驶辅助配置'
                item['item'] = '车身颜色' 
                item['version_id'] = vers['SpecId']
                item['version'] = version_cow[ind]['Value']
                item['standard_version'] = version_cow[ind]['Value']
                item['url'] = "http://price.pcauto.com.cn/m%s/config.html"%vers['SpecId']
                item['collect_date'] = now.strftime("%Y-%m-%d")
                item['karw'] = ' '.join([v['Name'] for v in vers['ColorList']])
                if paidang:
                    item['paidang'] = paidang[ind]['Value']
                else:
                    item['paidang'] = paidang
                yield item
                # print(item)

        if js_innercolors_text:
            js_innercolors_code = json.loads(js_innercolors_text)
            for ind, vers in enumerate(js_innercolors_code['body']['items']):
                item['classfy'] = '驾驶辅助配置'
                item['item'] = '内饰颜色'
                item['version_id'] = vers['SpecId']
                item['version'] = version_cow[ind]['Value']
                item['standard_version'] = version_cow[ind]['Value']
                item['url'] = "http://price.pcauto.com.cn/m%s/config.html"%vers['SpecId']
                item['collect_date'] = now.strftime("%Y-%m-%d")
                item['karw'] = ' '.join([v['Name'] for v in vers['innerColorList']])
                if paidang:
                    item['paidang'] = paidang[ind]['Value']
                else:
                    item['paidang'] = paidang

                yield item
                # print(item)