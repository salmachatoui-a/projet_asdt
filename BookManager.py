from Book import Book
from Review import Review

class BookManager:
    def __init__(self):
        self._books = []

    def add_book(self, new_book:Book):
        self._books.append(new_book)

    @property
    def books(self):
        return self._books.copy()
    
    def to_dict(self):
        return {"books": [book.to_dict() for book in self._books]}
    
    def from_dict(self, dico:dict) -> None:
        """
        Initialize a book manager from json import
        """
        for i in dico["books"]:
            new_book = Book(i["name"], i["link"], i["path"])
            new_book.token_count = i["token_count"]
            for r in i["reviews"]:
                new_review = Review(r["text"], r["rating"], 0) # 0 because the last export did not take into account the token count for serialization 
                new_book.add_review(new_review)
            self.add_book(new_book)