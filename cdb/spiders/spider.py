import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CdbItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CdbSpider(scrapy.Spider):
	name = 'cdb'
	start_urls = ['https://www.cdb.com.cy/news']

	def parse(self, response):
		articles = response.xpath('//div[@class="date_container bg-color-purple"]')
		for article in articles:
			date = [article.xpath('.//h4/text()').get()+' / '+ article.xpath('.//h6/text()').get()]
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post,cb_kwargs=dict(date=date))

	def parse_post(self, response,date):

		title = [response.xpath('//div[@class="container-content-inner"]/h3[@class="text-center small_section_title"]/text()').get() + response.xpath('//div[@class="container-content-inner"]/h1/text()').get()]
		content = response.xpath('//div[@itemprop="articleBody"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CdbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
