import sys
import furl as furl
import logging
import time
from selenium.webdriver.remote.remote_connection import LOGGER
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from selenium import webdriver


LOGGER.setLevel(logging.WARNING) # Selenium logging level
chromepath = 'C:/chromedriver/chromedriver.exe'  # //change this to your chromedriver path


def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        print('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def get_urls_and_price(link):
    html = simple_get(link)
    html = BeautifulSoup(html, 'html.parser')
    offers = html.find("div", {"class": "offers-table"})
    prices = offers.findAll("span", {"itemprop": "price"})
    urls = offers.findAll("a", {"class": "d-none d-xl-block buy-btn"})
    if len(urls) != len(prices):
        print("warning arrays don't match")
    link_and_price = {}
    for x in range(len(prices)):
        link_and_price[x] = {'link': urls[x]['href'], 'price': prices[x]['content']}
    return link_and_price


def average_price(link_and_price):
    counter = 0
    price_sum = 0.0
    for x in range(len(link_and_price)):
        price_sum = price_sum + float(link_and_price[x]['price'])
        counter = counter + 1
    return price_sum / counter


def lowest_price_link(link_and_price):
    lowest_price = link_and_price[0]['price']
    index = 0
    for x in range(len(link_and_price)):
        if link_and_price[x]['price'] < lowest_price:
            lowest_price = link_and_price[x]['price']
            index = x
    return link_and_price[index]


def get_redirected_url(url):
    driver = webdriver.Chrome(chromepath)
    driver.get("https:" + url)
    time.sleep(5)
    destination_url = driver.current_url
    driver.quit()
    return destination_url


def main():
    if len(sys.argv) != 2:
        print("You forgot to enter the name of the game as an argument.")
        print("Example: ./game_price_scraper.py \"Game Title\"")
        exit(1)

    search_phrase = sys.argv[1]
    print("Search Term:", search_phrase, "\n")
    search_phrase = search_phrase.lower()
    search_phrase = search_phrase.replace(" ", "-")

    url = "https://www.allkeyshop.com/blog/catalogue/search-"

    search_page_html = simple_get(url + search_phrase)

    search_page_html = BeautifulSoup(search_page_html, 'html.parser')
    search_results_row = search_page_html.findAll("li", {"class": "search-results-row"})
    links = {}
    for x in range(len(search_results_row)):
        game_link = search_results_row[x].select("a")
        game_title = search_results_row[x].select("h2")
        links[x] = {'link': game_link[0]['href'], 'title': game_title[0].text}

    for x in links:
        link_and_price = get_urls_and_price(links[x]['link'])
        average = average_price(link_and_price)
        lowest_link = lowest_price_link(link_and_price)
        destination_url = get_redirected_url(lowest_link['link'])
        clean_url = furl.furl(destination_url).remove(args=True, fragment=True).url
        print("Game:", links[x]['title'], "\nAverage price:", format(average, '.2f'), "\nLowest Price",
              lowest_link['price'],
              "\nLink:", clean_url, "\n")


if __name__ == '__main__':
    main()
