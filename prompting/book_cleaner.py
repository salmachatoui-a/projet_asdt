from gutenberg_cleaner import super_cleaner
import os

def clean_book(input_path:str):
    with open(input_path, "r", encoding='utf-8') as file:
        book = file.read()

    clean_book = super_cleaner(book)
    clean_book = clean_book.replace("[deleted]", "")

    output_path = os.path.join("clean-books", os.path.basename(input_path))

    with open(output_path, "w", encoding='utf-8') as file:
        file.write(clean_book)
    
    return output_path