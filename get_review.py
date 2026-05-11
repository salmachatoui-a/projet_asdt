from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from BookManager import BookManager
from Book import Book
from extract_books import get_driver
from Review import Review
from LangDetector import LangDetect
import time
import re

MAX_TOKEN = 2500

def scroll_down(driver, px = 30) -> None:
    driver.execute_script(f"window.scrollBy(0, {px});")

def clean_title(title: str) -> str:
    title = title.lower()

    # remove volume info
    title = re.sub(r"\bvolume\s*\d+\b", "", title)
    title = re.sub(r"\bvol\.?\s*\d+\b", "", title)

    # remove info in brackets  like (of 10)
    title = re.sub(r"\(.*?\)", "", title)

    # remove fancy dashes and weird separators
    title = title.replace("—", " ")
    title = title.replace("-", " ")
    title = title.replace(";", ":")

    # collapse spaces
    title = re.sub(r"\s+", " ", title).strip()

    return title

def clean_review(review:str = None) -> str:
    return review.strip().replace("\n", "")

def wait_and_remove_overlay(driver, timeout=10):
    try:
        overlay = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal--overlay"))
        )
        driver.execute_script("arguments[0].remove();", overlay)
    except:
        pass

def count_tokens(text:str) -> int:
    text = re.sub(r"\s+", " ", text).strip()
    return len(text.split())

def get_reviews(driver, link) -> list[Review]:
    def get_rating(review_card) -> str:
        try : 
            rating_elem = review_card.find_element(By.CSS_SELECTOR, ".RatingStars.RatingStars__small")
        except NoSuchElementException:
            return None

        rating = rating_elem.get_attribute("aria-label")
        pattern = r"Rating ([0-5]) out of 5"
        rating_search = re.search(pattern, rating)
        if rating_search:
            rating = rating_search.group(0)
        else:
            raise ValueError
        return rating
    def get_text(review_card) -> str:
        review_text = review_card.find_element(By.CLASS_NAME, "ReviewText__content")
        return review_text.text 

    driver.get(link)

    lang_detector = LangDetect()

    time.sleep(5)

    scroll_down(driver, 2500)

    review_cards = driver.find_elements(By.CLASS_NAME, "ReviewCard")    
    all_reviews = []
    total_tokens = 0
    for rc in review_cards:
        if total_tokens >= MAX_TOKEN:
            print("enough for this book")
            print(total_tokens)
            break

        new_rating, new_text = get_rating(rc), get_text(rc)
        if not lang_detector.is_eng(new_text):
            continue
        new_text = clean_review(new_text)
        total_tokens += count_tokens(new_text)
        new_review = Review(new_text, new_rating, total_tokens)
        all_reviews.append(new_review)
        scroll_down(driver, 700)
    print(f"{len(all_reviews)} for {link}")
    return all_reviews


def get_review_links(driver:webdriver, book_title:str):
    driver.get("https://www.goodreads.com/search")

    wait_and_remove_overlay(driver)
    #book_searchbar = WebDriverWait(driver, 1).until(
    #    EC.presence_of_element_located((By.ID, "search_query_main"))
    #)
    book_searchbar = driver.find_element(By.ID, "search_query_main")
    book_searchbar.clear()
    book_searchbar.send_keys(book_title)
    
    #search_btn = WebDriverWait(driver, 1).until(
    #    EC.element_to_be_clickable(
    #        (By.CSS_SELECTOR, ".searchBox__button.searchBox--large__button")
    #    )
    #)
    search_btn = driver.find_element(By.CSS_SELECTOR, ".searchBox__button.searchBox--large__button")
    wait_and_remove_overlay(driver)
    search_btn.click()
    try: 
        result_table = driver.find_element(By.TAG_NAME, "tbody")
        results = result_table.find_elements(By.XPATH, ".//*")
        result = results[0]
        reviews_link = result.find_element(By.TAG_NAME, "a")
        link = reviews_link.get_attribute("href")
        print(link)

        return link
    except NoSuchElementException:
        print(f"Book {book_title} not found in goodreads")
        return None
