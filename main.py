import json
import get_review
import datetime
from BookManager import BookManager
from Book import Book

def load_bookmanager(path:str) -> BookManager:
    with open(path, "r", encoding='utf-8') as file:
        ok = json.load(file)
    book_manager = BookManager()
    for b in ok["books"]:
        new_book = Book(name=b["name"], link=b["link"], path=b["path"])
        book_manager.add_book(new_book)
    return book_manager

print(f"{datetime.datetime.now()} getting book names")
book_manager = load_bookmanager("./book_manager.json")
driver = get_review.get_driver()

try:
    print(f"{datetime.datetime.now()} getting reviews")
    for i, book in enumerate(book_manager.books, 1):
        print(f"[{i}] {book.name}")

        title = get_review.clean_title(book.name)
        review_link = get_review.get_review_links(driver, title)
        if review_link is not None:
            reviews = get_review.get_reviews(driver, review_link)
            for r in reviews:
                book.add_review(r)
        else:
            print(f"{title} no reviews")

finally:
    driver.quit()

print(f"{datetime.datetime.now()} writing file")

with open("./all_reviews.json", "w", encoding="utf-8") as file:
    json.dump(
        book_manager.to_dict(),
        file,
        indent=4,
        ensure_ascii=False
    )