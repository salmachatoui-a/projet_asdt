from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from BookManager import BookManager
from Book import Book
import re
import wget
import os
import json
import time

def strip_count(title:str):
    pattern = re.compile(r'\(\d+\)')
    return re.sub(pattern, '', title)

def get_driver() -> webdriver:
    service = Service(executable_path=r'/usr/bin/geckodriver')
    options = webdriver.FirefoxOptions()
    #options.add_argument("--headless")
    options.binary_location = r'/usr/bin/firefox'
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    return driver

import requests

def download_with_session(driver, url, output_path):
    session = requests.Session()

    # copy cookies from selenium
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = session.get(url, headers=headers, stream=True)

    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}")

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return output_path

def dl_book(driver, url:str, title:str, retries:int = 3) -> str:
    title = title.replace(" ", "_")
    title = title.replace(";", "")
    title = title.replace(",", "")
    for attempt in range(retries):
        print(f"[{attempt+1}] Opening {title}")
        try:
            driver.get(url)
            dl_table = driver.find_element(By.ID, "download_options_table").find_element(By.TAG_NAME, "tbody")
            for dl_option_row in dl_table.find_elements(By.XPATH, ".//*"):
                if dl_option_row.text == "Plain Text UTF-8":
                    dl_option_row.find_element(By.TAG_NAME, "a").click()
                    link = driver.current_url
                    print("ok url")
                    output_path = os.path.join("dump", title + ".txt")
                    if os.path.exists(output_path):
                        print("already dl")
                    else:
                        download_with_session(driver, link, output_path)
                    #wget.download(link, output_path)
                    return output_path
        except Exception as e:
            print("ERROR : ", e)
            if "session" in str(e).lower():
                print("Driver died → restarting")
                driver.quit()
                driver = get_driver()
            time.sleep(3 * (attempt + 1))
    print("FAILED:", title)
    return None

def get_book_info(driver):
    driver.get("https://www.gutenberg.org/browse/scores/top")

    top100 = driver.find_elements(By.XPATH, "/html/body/div[1]/div/ol[1]")

    book_titles = top100[0].text.split("\n")
    book_titles = list(map(strip_count, book_titles))

    book_links_element = top100[0].find_elements(By.XPATH, ".//*")
    book_links = [elem.get_attribute('href') for elem in book_links_element]
    book_links = list(filter(lambda x : x is not None, book_links))

    return book_titles, book_links

def main():
    driver = get_driver()
    book_titles, book_links = get_book_info(driver)

    book_manager = BookManager()
    for title, link in zip(book_titles, book_links):
        print(title, link)
        book_path = dl_book(driver, link, title)
        new_book = Book(title, link, book_path)
        book_manager.add_book(new_book)
    driver.quit()
    return book_manager

if __name__ == "__main__":
    book_manager = main()
    with open("book_manager.json", "w", encoding='utf-8') as file:
        json.dump(book_manager.to_dict(), file, ensure_ascii=False, indent=4)