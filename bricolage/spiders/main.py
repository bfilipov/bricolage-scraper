# -*- coding: utf-8 -*-
import scrapy


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        if len(response.xpath("//div[@class='sort-refine-bar']")) > 0:  # list page identifier
            for item in response.xpath("//div[@class='product']")[0:2]:

                product = {
                    'title_list':''.join(
                        e for e in item.
                        xpath(".//div[@class='title']/a/text()").extract_first() if (e.isalnum() or e == ' ')
                    ),
                    'price_list':item.xpath(".//div[@class='price']/text()").extract_first(),
                    'image_list':response.urljoin(item.xpath(".//div[@class='image']/a/img/@src").extract_first())
                }
                request = scrapy.Request(
                    url=response.urljoin(item.xpath(".//div[@class='image']/a/@href").extract_first()),
                    callback=self.parse_product_page,
                    #dont_filter=True
                )
                request.meta['product'] = product
                yield request


        next_page = response.xpath("//li[@class='pagination-next']/a/@href").extract_first()
        # if next_page is not None:
        #     next_page=response.urljoin(next_page)
        #     yield scrapy.Request(
        #         next_page,
        #         callback=self.parse,
        #         #dont_filter=True
        #     )

    def parse_product_page(self, response):
        product = response.meta['product']
        csrf_token = response.xpath("//input[@name='CSRFToken']/@value").extract_first()
        cookie = response.headers.getlist('Set-Cookie')[0].decode("utf-8")
        bricolage_id = response.xpath("//div[@class='col-md-12 bricolage-code']/text()")\
            .extract_first().split(":")[1].strip()

        yield product

        request = scrapy.Request(
            method='POST',
            url='https://mr-bricolage.bg/store-pickup/{}/pointOfServices?locationQuery=&cartPage=false&entryNumber=0&latitude=42.6641056&longitude=23.3233149&CSRFToken={}'.format(bricolage_id, csrf_token),
            headers={
                'accept':'*/*',
                'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent':' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                'Cookie': cookie.split(";")[0],
            },
            callback=self.parse_json_request
        )

        yield request

    def parse_json_request(self, response):

        self.logger.info(
            response.body
        )
        #import pdb;  pdb.set_trace()
