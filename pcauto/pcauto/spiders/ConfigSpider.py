# -*- coding: utf-8 -*-
import scrapy , datetime, json, requests
from scrapy.selector import Selector
from scrapy.shell import inspect_response
from pcauto.items import DealerItem
from pcauto.get_page import get_pages

class ConfigSpider(scrapy.Spider):
    name = 'pcautoDealer'
    baseurl = 'http://price.pcauto.com.cn'
    test_url = "http://price.pcauto.com.cn/98473/"

    def start_requests(self):
        url = 'http://price.pcauto.com.cn/shangjia/c0/'
        yield scrapy.Request(url=url, callback=self.dealer_list, dont_filter=True)

    # FOR TEST
    # def start_requests(self):
    #     url = 'http://price.pcauto.com.cn/shangjia/c0/'
    #     yield scrapy.Request(url=self.test_url, callback=self.dealer_info_not4s, dont_filter=True)

    def dealer_list(self, response):
        sel = Selector(response)
        meta = {}
        ul = sel.xpath("//ul[@class='yStore clearfix']/li")
        for li in ul:
            name = li.xpath("div[@class='divYSd']/p")[0].xpath("a/@title").extract_first()
            addr = li.xpath("div[@class='divYSd']/p")[2].xpath("span/@title").extract_first()
            localtion = li.xpath("div[@class='divYSd']/p")[0].xpath("span[@class='smoke']/text()").extract_first()
            dealer_id = li.xpath("div[@class='divYSd']/p")[0].xpath("a/@href").extract_first().split('/')[-2]
            url = '%s/%s/'%(self.baseurl, dealer_id)
            meta.update({
                'name':name,
                'address':addr,
                'localtion':localtion,
                'dealer_id':dealer_id,
                'url':url,
                })

            icon_4s = li.xpath("div[@class='divYSd']/p")[0].xpath("span/@class").extract()
            if 'icon icon-jxs-green' in icon_4s:
                yield scrapy.Request(url=url, meta=meta, callback=self.dealer_info, dont_filter=True)
            else:
            # elif 'icon icon-jxs-grey' in icon_4s:
                yield scrapy.Request(url=url, meta=meta, callback=self.dealer_info_not4s, dont_filter=True)

        if sel.xpath("//div[@class='pcauto_page']/div/a[@class='next']"):
            next_page = sel.xpath("//div[@class='pcauto_page']/div/a[@class='next']/@href").extract_first()
            url = '%s%s'%(self.baseurl, next_page)
            
            yield scrapy.Request(url=url, meta=meta, callback=self.dealer_list, dont_filter=True)


    def dealer_info(self, response):
        sel = Selector(response)
        meta = response.meta
        info = sel.xpath("//div[@class='logotext']/p/em/text()").extract_first()
        brand = sel.xpath("//div[@class='pic-txt']")[0].xpath('string(.)').extract_first().strip()
        meta.update({'info':info,
                    'brand':brand,
                    })

        url = '%smodel.html'%meta['url']

        request = scrapy.Request(url=url, meta=meta, callback=self.parse_4s, dont_filter=True)
        # request.meta['PhantomJS'] = True
        yield request

    def parse_4s(self, response):

        sel = Selector(response)
        meta = response.meta

        page_max = get_pages(response.text)
        if page_max:
            for p in range(1,int(page_max)+1):
                url = response.url.split('model.html')[0]+'p%s/model.html#model'%str(p)
                yield scrapy.Request(url=url, meta=meta, callback=self.parse_item_4s, dont_filter=True)

    def parse_item_4s(self, response):

        # inspect_response(response, self)
        sel = Selector(response)
        meta = response.meta
        item = DealerItem()
        dl = sel.xpath("//dl[@class='tjlist allchex clearfix']/dd")
        for dd in dl:
            item['model'] = dd.xpath("div[@class='autobox']/span/a/text()").extract_first()
            carbox = dd.xpath("dl/dl")
            for car in carbox:
                dd = car.xpath("dd")
                for ob in dd:
                    item['version_name'] = ob.xpath("div")[0].xpath("a/text()").extract_first()
                    version_url = ob.xpath("div")[0].xpath("a/@href").extract_first()
                    item['version_id'] = version_url.split('/')[-2]
                    item['msrp'] = ob.xpath("div")[1].xpath("text()").extract_first()
                    item['sale'] = ob.xpath("div")[2].xpath("text()").extract_first().strip()
                    item['name'] = meta['name']
                    item['address'] = meta['address']
                    item['localtion'] = meta['localtion']
                    item['dealer_id'] = meta['dealer_id']
                    item['url'] = meta['url']
                    item['info'] = meta['info']
                    item['brand'] = meta['brand']
                    now = datetime.datetime.now()
                    item['collect_date'] = now.strftime("%Y-%m-%d")
                    print(item['version_name'])
                    print(item['name'])
                    print(item['url'])
                    yield item

    def dealer_info_not4s(self, response):
        sel = Selector(response)
        meta = response.meta
        item = DealerItem()
        item['name'] = meta['name']
        item['address'] = meta['address']
        item['localtion'] = meta['localtion']
        item['dealer_id'] = meta['dealer_id']

        request_url="http://price.pcauto.com.cn/dealer/interface/dealer_free_info_json.jsp?m=getSgByDealer&did=%s&maid=%s&sgid=0&pageNo=%s"
        model_ids = sel.xpath("//input[@type='hidden'][@value='1']/@id").extract()
        item['info'] = sel.xpath("//div[@class='txt']/div/a/@title").extract_first()
        for pageno in model_ids:
            model_id = pageno.split('_')[-1]
            n = 1
            while 1:
                js_text = requests.get(request_url%(meta['dealer_id'], model_id, str(n)))
                js_code = json.loads(js_text.text)
                # print(js_code.values())
                if js_code.get('result'):
                    data = js_code['data']
                    for car in data:
                        priceRange = car['priceRange']
                        item['msrp'] = "%s-%s"%(priceRange['minPrice'], priceRange['maxPrice'])
                        name = car['name']
                        item['brand'] = ''.join(name.split('-')[:-1])
                        item['model'] = name.split('-')[-1]
                        item['version_id'] = ''
                        item['version_name'] = ''
                        item['sale'] = ''
                        item['url'] = response.url
                        now = datetime.datetime.now()
                        item['collect_date'] = now.strftime("%Y-%m-%d")
                        yield item
                    n += 1
                else:
                    break