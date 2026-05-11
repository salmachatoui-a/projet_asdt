class Review:
    def __init__(self, text:str, rating:str, tokens_count:int):
        self.text = text
        self.rating = rating
        self.tokens_count = tokens_count
    
    def to_json(self):
        return {"text" : self.text, "rating" : self.rating, "tokens_count" : self.tokens_count}