import json

from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess

from foodpanda_parser import FoodPandaParser

class FoodPandaCrawlSpider(Spider):
    name = "foodpanda-crawl"
    start_urls = ["https://www.foodpanda.pk/city/lahore"]
    parse_spider = FoodPandaParser()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML," \
            " like Gecko) Chrome/121.0.0.0 Safari/537.36",
    }
    
    def start_requests(self):
        return [Request(self.start_urls[0], headers=self.headers)]
    
    def parse(self, response):
        css = "script:contains(ItemList)::text"
        raw_restaurants = json.loads(response.css(css).get())["itemListElement"]
        raw_restaurants = [restaurant['item']['url'] for restaurant in raw_restaurants]

        yield from [response.follow(url, self.parse_reviews, headers=self.headers) for url in raw_restaurants]
        
    def parse_reviews(self, response):
        yield from self.parse_spider.parse(response)


if __name__ == '__main__':
    pipelines = {
        "pipelines.LowerCasePipeline": 1,
        "pipelines.RemovePunctuationPipeline": 2,
        "pipelines.StripStringPipeline": 3,
    }

    process = CrawlerProcess(settings={
        "DOWNLOAD_DELAY": 10,
        "CONCURRENT_REQUESTS": 1,
        "HTTPERROR_ALLOWED_CODES": [403],
        "ITEM_PIPELINES": pipelines
    })
    process.crawl(FoodPandaCrawlSpider)
    process.start()