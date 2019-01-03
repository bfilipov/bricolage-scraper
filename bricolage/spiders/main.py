# -*- coding: utf-8 -*-
import scrapy


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['https://mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        for item in response.xpath("//div[@class='product']"):
            yield {
                'title': item.xpath(".//div[@class='title']/a/text()").extract_first(),
                'price': item.xpath(".//div[@class='price']/text()").extract_first(),
                'image': item.xpath(".//div[@class='image']/a/img/@src").extract_first(),
            }

        next_page = response.xpath("//li[@class='pagination-next']").extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

