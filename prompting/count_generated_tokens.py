import os

def missing_tokens(dir_path:str = "synced_reviews"):
    paths = os.listdir(dir_path)
    paths = [os.path.join(dir_path, p) for p in paths]

    all_reviews = []
    total_tokens = 0
    for p in paths:
        with open(p, "r", encoding='utf-8') as file:
            review = file.read()
            all_reviews.append(review)
        count = len(review.split())
        total_tokens += count
    return total_tokens, len(all_reviews)