import sys
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup


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
    a = html.find("div", {"class": "offers-table"})
    d = a.findAll("span", {"itemprop": "price"})
    z = a.findAll("a", {"class": "d-none d-xl-block buy-btn"})
    if len(z) != len(d):
        print("warning arrays don't match")
    link_and_price = {}
    for x in range(len(d)):
        link_and_price[x] = {'link': z[x]['href'], 'price': d[x]['content']}
    return link_and_price


def average_price(link_and_price):
    counter = 0
    sum = 0.0
    for x in range(len(link_and_price)):
        sum = sum + float(link_and_price[x]['price'])
        counter = counter + 1
    return sum / counter


def lowest_price_link(link_and_price):
    lowestPrice = link_and_price[0]['price']
    index = 0
    for x in range(len(link_and_price)):
        if link_and_price[x]['price'] < lowestPrice:
            lowestPrice = link_and_price[x]['price']
            index = x
    return link_and_price[index]
