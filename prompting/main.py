import random 
import os
import re
import threading
import subprocess
import datetime
from ollama import chat
from ollama import ChatResponse
from book_cleaner import clean_book
from count_generated_tokens import missing_tokens

sync_lock = threading.Lock()

def sync_file():
    if not sync_lock.acquire(blocking=False):
        return # Skip if syncing is already running

    try:
        subprocess.run(["sh", "./sync.sh"])
        print(f"sync done {datetime.datetime.now()}")
    finally:
        sync_lock.release()

def basename_no_extension(path:str):
    "Returns filename without file type extension"
    return os.path.splitext(os.path.basename(path))[0]

def count_tokens(text:str) -> int:
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())

def trim_book(book_str:str, size:int = 20000) -> str:
    """
    Truncate the book so it's lighter and the prompt and the model can have better context consideration.
    """
    return book_str[:size//2] + "\n\n...[TRUNCATED]...\n\n" + book_str[-size//2:]

def get_book(path:str) -> str:
    "Reads book from path"
    with open(path, "r", encoding='utf-8') as file:
        book_text = file.read()
    return book_text

def make_prompt(book_str:str) -> str:
    "Make a prompt that will be given to the model"
    intro_variants = [
    "Write a natural book review based on the text below.",
    "Give a spontaneous human review of the following book.",
    "Write a casual but thoughtful review of this book.",
    "React to this book as if you just finished reading it."
    ]
    prompt = f"""
    {random.choice(intro_variants)}

    You are reading the FULL book below, it may be long.

    Do not assume missing content.

    --- BOOK START ---
    {book_str}
    --- BOOK END ---
    """
    return prompt

def generate_review(book_path:str) -> int:
    book = trim_book(get_book(book_path))
    prompt = make_prompt(book)

    response : ChatResponse = chat(model='mistral-nemo:12b', 
    messages =[
    {
        'role': 'user',
        'content': prompt,
    },
    ],
    options={"num_ctx": 8192,"num_predict" : 800})
    output = response.message.content
    
    book_filename = os.path.basename(book_path)
    export_path = os.path.join("generated_reviews", book_filename)

    i = 1
    name = basename_no_extension(book_path)
    while os.path.exists(export_path):
        export_path = os.path.join("generated_reviews", f"{name}-{i}.txt")
        i += 1

    with open(export_path, "w", encoding='utf-8') as file:
        file.write(output)
    
    return count_tokens(output)

def main(path_list:list, current_tokens:int):
    total_tokens = current_tokens
    MAX_TOKENS = 250000
    token_goal = MAX_TOKENS - current_tokens

    print("Beginning generation")
    while total_tokens <= MAX_TOKENS:
        for path in path_list:
            total_tokens += generate_review(path)
            if not sync_lock.locked():
                threading.Thread(target=sync_file).start()
            print(f"{total_tokens} current book : {path}")
            print(f"{MAX_TOKENS-total_tokens} left")
            if total_tokens > token_goal:
                print("Enough tokens reached!")
                print(f"{total_tokens} tokens")
                break

if __name__ == "__main__":
    path_list = os.listdir("../dump")
    path_list = [os.path.join("../dump", f) for f in path_list]

    clean_book_path_list = []
    for f in path_list:
        clean_book_path = clean_book(f)
        clean_book_path_list.append(clean_book_path)

    current_tokens, review_count = missing_tokens("synced_reviews")
    print(f"{current_tokens} tokens, {250000-current_tokens} left to generate")
    main(clean_book_path_list, current_tokens)