 # -*- coding: utf-8 -*-
import scrapy , datetime, json, requests, re, random
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from xcar.items import XcarItem

class CongfigSpider(scrapy.Spider):
    name = 'xcar_config'

    def start_requests(self):

        url  = "http://newcar.xcar.com.cn/price/"

        yield scrapy.Request(
                url = url,
                callback=self.model_list,
                dont_filter=True,
            )

    def model_list(self, response):
        # inspect_response(response, self)
        sel = Selector(response)
        model_list = sel.xpath("//div[@id='img_load_box']/div/table/tbody/tr")
        for item in model_list:
            brand = item.xpath("td/div/a/img/@title").extract_first()
            for model in item.xpath("td/div/ul/li/div/a/@href").extract():
                url = "http://newcar.xcar.com.cn%s"%model
                meta = {'brand':brand,'model':model.strip('/')}

                yield scrapy.Request(
                    url=url,
                    meta=meta,
                    callback=self.car_parse,
                    dont_filter=True,
                    )

    def car_parse(self, response):
        sel = Selector(response)
        meta = response.meta
        model_name = sel.xpath("//div[@class='tt_h1']/h1/text()").extract_first()
        meta['model_name'] = model_name
        years = sel.xpath("//div[@class='stop_pop']/ul/li/a/@data").extract()
        version_ids = sel.xpath("//table[@class='modellist_open table_main']/tbody/tr[@class='table_bord']/td[1]/p/a/@href").extract()
        rand = random.random()
        for year in years:
            json_url = "http://newcar.xcar.com.cn/auto/index.php?r=newcar/SeriseParentIndex/AjaxStopSaleModel&rand=%s&pserid=%s&year=%s"%(rand,meta['model'],year)
            res = requests.get(json_url, headers={'X-Requested-With':'XMLHttpRequest'})
            page = Selector(res)
            notsale = sel.xpath("//table[@class='table_main']/tbody/tr[@class='table_bord']/td[1]/p/a/@href").extract()
            version_ids.extend(notsale)

        for v_id in version_ids:
            url = "http://newcar.xcar.com.cn%sconfig.htm"%v_id
            meta['version_id'] = v_id.strip('/')

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
        sel = Selector(response)
        item = XcarItem()
        meta = response.meta

        idx = {}
        tr = sel.xpath("//table[@id='Table1']/tr")
        for i in tr:
            if i.xpath('@class').extract_first() == 'config_base_title':
                k = tr.index(i)
                v = i.xpath('th/text()').extract_first().strip('：')
                idx[k] = v

        for i in tr:
            if i.xpath('*')[0].xpath('string(.)').extract_first().strip() == '变速箱类型：':
                paidang_line = i.xpath('*')[1:].xpath('string(.)').extract_first().strip()

        version_name = sel.xpath("//span[@class='lt_f1']/text()").extract_first() + sel.xpath("//h1/text()").extract_first()
        for index, row in enumerate(tr):
            if index in idx:
                pass
            else:
                title = self.chooseline(index,idx)
                ll = row.xpath('*')[1].xpath('string(.)').extract_first().strip().strip('：')
                th = row.xpath('*')[0].xpath('string(.)').extract_first().strip()
                item['paidang'] = paidang_line
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
                model_name = meta['model_name']
                item['standard_version'] = '%s %s'%(model_name,version_name)

                yield item
                # print(item)