# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, http
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class CarconfigSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PhantomJSMiddleware(object):
    @classmethod
    def process_request(cls, request, spider):

        #2.7
        # if request.meta.has_key('PhantomJS'):
        #3
        if 'PhantomJS' in request.meta:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
            'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
            )


            driver = webdriver.PhantomJS(executable_path="D:\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe",
                        desired_capabilities=dcap
                            )
# http://car.autohome.com.cn/config/series/script/config-min.js?v=201709041522
           
            # driver.set_page_load_timeout(10)
            # while True:         
            #     try:
            #         driver.get(request.url)
            #         time.sleep(1)
            #     except:
            #         pass
            #         #driver.execute_script('window.stop()')
            #     else:
            #         break

            driver.get(request.url)
            content = driver.page_source.encode('utf-8')
            driver.quit()  
            return http.HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
