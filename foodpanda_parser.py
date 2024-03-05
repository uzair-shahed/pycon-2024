import json
import re

from scrapy import Request, Spider
from scrapy.item import Item, Field
from w3lib.url import add_or_replace_parameters

class Review(Item):
    id = Field()
    name = Field()
    content = Field()
    date = Field()
    restaurant_name = Field()
    restaraunt_id = Field()

    customer_rating = Field()
    worst_rating = Field()
    best_rating = Field()
    
    tokens = Field()


class FoodPandaParser(Spider):
    name = "foodpanda-spider"
    parse_url = "https://www.foodpanda.pk/restaurant/q3tt/subway-dha-eme"
    review_api_url = "https://reviews-api-pk.fd-api.com/reviews/vendor/{restaurant_id}"
    review_api_params = {
        "global_entity_id": "FP_PK",
        "limit": "30",
    }

    def parse(self, response):
        if not (name_raw := response.css('[type="application/ld+json"] ::text').get()):
            return []
        
        restaurant_id = re.findall(r"\/restaurant\/(.*?)\/", response.url)[0]
        review_api_url = self.review_api_url.format(restaurant_id=restaurant_id)
        review_api_url = add_or_replace_parameters(review_api_url, self.review_api_params)
        
        review = Review()
        review['restaurant_name'] = json.loads(name_raw)['name']
        review['restaurant_id'] = restaurant_id

        return [Request(review_api_url, self.parse_reviews, meta={'review': review})]

    def parse_reviews(self, response):
        review_data = json.loads(response.text)['data']
        review = response.meta['review']

        for data in review_data:
            review = review.copy()
            review['id'] = data['uuid']
            review['name'] = data['reviewerName']
            review['content'] = data['text']
            review['date'] = data['createdAt']
            review['customer_rating'] = [x['score'] for x in data['ratings'] if x['topic'] == 'overall'][0]
            review['worst_rating'] = 1
            review['best_rating'] = 5
            yield review
        
        yield from self.review_pagination(response)

    def review_pagination(self, response):
        if page_key := json.loads(response.text).get('pageKey'):
            params = self.review_api_params.copy()
            params['nextPageKey'] = page_key
            review_api_url = add_or_replace_parameters(response.url, params)
            return [Request(review_api_url, self.parse_reviews)]
        
        return []


