# -*- coding: utf-8 -*-
import scrapy
import re
from decimal import Decimal


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        if len(response.xpath("//div[@class='sort-refine-bar']")) > 0:  # list page identifier
            for item in response.xpath("//div[@class='product']"):
                title = ''.join(
                    e for e in item.xpath(".//div[@class='title']/a/text()").
                        extract_first() if (e.isalnum() or e == ' ')
                )
                price = item.xpath(".//div[@class='price']/text()").extract_first()

                price = '{0:.2f}'.format(
                    Decimal(re.sub(r'[^\d,]', '', price).replace(',', '.'))
                )
                image = response.urljoin(item.xpath(".//div[@class='image']/a/img/@src").extract_first())
                product = {
                    'title_list': title,
                    'price_list': price,
                    'image_list': image
                }
                request = scrapy.Request(
                    url=response.urljoin(item.xpath(".//div[@class='image']/a/@href").extract_first()),
                    callback=self.parse_product_page,
                )
                request.meta['product'] = product
                yield request

        next_page = response.xpath("//li[@class='pagination-next']/a/@href").extract_first()
        if next_page is not None:
            next_page=response.urljoin(next_page)
            yield scrapy.Request(
                next_page,
                callback=self.parse,
            )

    def parse_product_page(self, response):

        product = response.meta['product']

        # scrape selectors
        csrf_token = response.xpath("//input[@name='CSRFToken']/@value").extract_first()
        cookie = response.headers.getlist("Set-Cookie")[0].decode("utf-8")
        bricolage_id = response.xpath("//div[@class='col-md-12 bricolage-code']/text()").\
            extract_first().split(":")[1].strip()
        sap_ean = re.sub(
            r'[^\d]', '', str(response.xpath("//div[@class='product-classifications']/parent::div/div/span").extract_first())
        )
        product_specs = re.sub(
            r'\r|\n|\t|class="attrib"|\xa0', '',
            str(response.xpath("//div[@class='product-classifications']/table/tbody").extract_first())
        )
        title = response.xpath("//div[@class='col-md-6']/div[@class='row']/div[@class='col-md-6']/h1/text()")\
            .extract_first()

        price = '{0:.2f}'.format(
            Decimal(re.sub(r'\r|\n|\t|[^\d,]', '', response.xpath("//div[@class='col-md-12 price']/p/text()")
                           .extract_first()).replace(',', '.'))
        )

        # save the needed ones to dict
        product['product_specs'] = product_specs
        product['bricolage_id']  = bricolage_id
        product['title_product'] = title
        product['price_product'] = price
        product['sap_ean']       = sap_ean

        request = scrapy.Request(
            method='POST',
            url='https://mr-bricolage.bg/store-pickup/{}/pointOfServices'.format(bricolage_id) +
                '?locationQuery=&cartPage=false&entryNumber=0&latitude=42.6641056&longitude=23.3233149&' +
                'CSRFToken={}'.format(csrf_token),
            headers={
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/' +
                              '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
                'Cookie': cookie.split(";")[0],
            },
            callback=self.parse_json_request
        )
        request.meta['product'] = product
        yield request

    def parse_json_request(self, response):

        product = response.meta['product']
        product['available_in_stores'] = re.sub(
            r'\r|\n|\t', '', response.body.decode("utf-8")
        )
        self.logger.info(
            product
        )
        yield product
        #import pdb;pdb.set_trace()