from Review import Review

class Book:
    def __init__(self, name:str, link:str, path:str):
        self.name:str = name
        self.link:str = link
        self.path:str = path
        self.reviews:list[Review] = []
        self.token_count:int = 0
    
    def add_review(self, new_review:Review) -> None:
        self.reviews.append(new_review)
        self.token_count += new_review.tokens_count

    def to_dict(self):
        return {
            "name": self.name,
            "link": self.link,
            "path": self.path,
            "token_count": self.token_count,
            "reviews": [r.to_json() for r in self.reviews]
        }