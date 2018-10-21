from functions import *

if len(sys.argv) != 2:
    print("You forgot to enter the name of the game as an argument.")
    print("Example: ./script GameTitle")
    exit(1)

GameTitle = sys.argv[1]
print("Search Term:", GameTitle, "\n")
GameTitle = GameTitle.lower()
GameTitle = GameTitle.replace(" ", "-")

url = "https://www.allkeyshop.com/blog/catalogue/search-"
search_page_html = simple_get(url + GameTitle)

search_page_html = BeautifulSoup(search_page_html, 'html.parser')
search_results_block = search_page_html.findAll("li", {"class": "search-results-row"})
links = {}
for x in range(len(search_results_block)):
    j = search_results_block[x].select("a")
    i = search_results_block[x].select("h2")
    links[x] = {'link': j[0]['href'], 'title': i[0].text}

for x in links:
    link_and_price = get_urls_and_price(links[x]['link'])
    average = average_price(link_and_price)
    lowest_link = lowest_price_link(link_and_price)
    print("Game:", links[x]['title'], "\nAverage price:", format(average, '.2f'), "\nLowest Price",
          lowest_link['price'],
          "\nLink:", "https:" + lowest_link['link'], "\n")
