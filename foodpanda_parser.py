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
    restaraunt = Field()

    overall_rating = Field()
    worst_rating = Field()
    best_rating = Field()
    
    tokens = Field()


class FoodPandaParser(Spider):
    name = "foodpanda-spider"
    parse_url = "https://www.foodpanda.pk/restaurant/q3tt/subway-dha-eme"
    review_api_url = "https://reviews-api-pk.fd-api.com/reviews/vendor/{restaraunt_code}"
    review_api_params = {
        "global_entity_id": "FP_PK",
        "limit": "30",
    }
    headers = {
        "user-agent": "Postman"
    }

    def parse(self, response):
        restaraunt_code = re.findall(r"\/restaurant\/(.*?)\/", response.url)[0]
        review_api_url = self.review_api_url.format(restaraunt_code=restaraunt_code)
        review_api_url = add_or_replace_parameters(review_api_url, self.review_api_params)
        
        return [Request(review_api_url, self.parse_reviews, headers=self.headers)]

    def parse_reviews(self, response):
        review_data = json.loads(response.text)['data']

        for data in review_data:
            review = Review()
            review['id'] = data['uuid']
            review['name'] = data['reviewerName']
            review['content'] = data['text']
            review['date'] = data['createdAt']
            review['overall_rating'] = [x['score'] for x in data['ratings'] if x['topic'] == 'overall'][0]
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



    

# class TokenizationPipeline:
#     def process_item(self, review, spider):
#         review['tokens'] = nltk.word_tokenize(review['content'])
#         return review
    




# class RemoveStopWordsPipeline:
#     def process_item(self, review, spider):
#         stop_words = set(stopwords.words('english'))
#         review['tokens'] = [word for word in review['tokens'] if word.lower() not in stop_words]
#         return review


# class LemmatizationPipeline:
#     def process_item(self, review, spider):
#         lemmatizer = WordNetLemmatizer()
#         review['tokens'] = [lemmatizer.lemmatize(word) for word in review['tokens']]
#         return review


def clean(list_of_text):

    if not isinstance(list_of_text, list):
        raise ValueError(f"The clean() method only accepts lists")
    
    list_of_text = [text.replace('\n', '') for text in list_of_text]
    list_of_text = [text.replace('  ', ' ') for text in list_of_text]
    
    return list_of_text


