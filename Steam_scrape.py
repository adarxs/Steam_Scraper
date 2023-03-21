from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import requests
import os


def get_links():
    """retrieve links from the site"""
    log_file_name = 'sel.log'

    if os.path.exists(log_file_name):
        os.remove(log_file_name)

    logging.basicConfig(filename=log_file_name, level=logging.INFO,
                        format='%(levelname)s - %(message)s')

    url = "https://store.steampowered.com/category/rpg/"

    ua_random = UserAgent().random
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={ua_random}")
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_window_size(1024, 3000)
    driver.get(url)

    wait = WebDriverWait(driver, 10)

    element_present = EC.presence_of_element_located((By.CLASS_NAME, "salepreviewwidgets_SaleItemBrowserRow_y9MSd"))
    wait.until(element_present)

    page_source = driver.page_source
    driver.quit()

    rpgs_soup = BeautifulSoup(page_source, 'lxml')

    outer_games_divs = rpgs_soup.find_all('div', class_="salepreviewwidgets_SaleItemBrowserRow_y9MSd")

    links = []
    for outer_games_div in outer_games_divs:
        inner_game_div = outer_games_div.find('div', class_="salepreviewwidgets_StoreSaleWidgetHalfLeft_2Va3O")
        img_tag = outer_games_div.find('img', class_='salepreviewwidgets_CapsuleImage_cODQh')
        name = img_tag['alt']
        link = inner_game_div.a['href']
        links.append(link)
    return links


def convert_to_price(arr):
    """convert price representation to regular price representation"""
    help_arr = []
    for x in arr:
        if x.isnumeric() or x == '.' or x == '₪':
            help_arr.append(x)
    return "".join(help_arr)


def strip_release_dates(date_str: str):
    """convert release date representation to regular date representation"""
    return date_str.strip("Release Date:").replace('\n', '')


INFO_DICT = {'game_names': [], 'prices': [], 'release_dates': []}  # Global INFO dictionary


def print_info(link):
    """prints single movie info and updated INFO_DICT"""
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    release = soup.find_all("div", class_="release_date")
    price = soup.find("div", class_="game_purchase_price price")
    name = soup.find("div", class_="apphub_AppName")

    if name is not None:
        for n in name:
            print("Name:\n", n.text.strip())
            INFO_DICT['game_names'].append(n)
            if release is not None:
                for r in release:
                    print(r.text.strip())
                    INFO_DICT['release_dates'].append(f"{n}: {strip_release_dates(r.text.strip())}")
            if price is not None:
                for p in price:
                    print("Price:\n", convert_to_price([x for x in p.text.strip()]))
                    INFO_DICT['prices'].append(f"{n}: {convert_to_price([x for x in p.text.strip()])}")


def print_all_info():
    """prints info of all movies."""
    for link in get_links():
        print_info(link)


def show_info_dict():
    """prints INFO_DICT"""
    print(INFO_DICT)
    print(len(INFO_DICT['game_names']))

def main():
    print_all_info()
    show_info_dict()

if __name__ == '__main__':
    main()
