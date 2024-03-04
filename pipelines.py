import string


class LowerCasePipeline:
    def process_item(self, review, spider):
        review['content'] = review['content'].lower()
        return review
    

class RemovePunctuationPipeline:
    def process_item(self, review, spider):
        review['content'] = review['content'].translate(str.maketrans('', '', string.punctuation))
        return review
    

class StripStringPipeline:
    def process_item(self, review, spider):
        review['content'] = review['content'].strip()
        return review