# -*- coding: utf-8 -*-
import scrapy


class MainSpider(scrapy.Spider):
    name = 'main'
    allowed_domains = ['mr-bricolage.bg']
    start_urls = ['mr-bricolage.bg/bg/Каталог/Инструменти/Авто-и-велоаксесоари/Велоаксесоари/c/006008012']

    def parse(self, response):
        pass
