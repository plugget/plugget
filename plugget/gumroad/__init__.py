import requests
from bs4 import BeautifulSoup


def get_gumroad_rating(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    rating_elem = soup.find('div', class_='rating')
    rating = rating_elem.find('div', class_='rating-average').text.strip()
    return float(rating)


def get_products():
    import requests

    access_token = "ACCESS_TOKEN"
    url = "https://api.gumroad.com/v2/products"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        products = response.json()
        for product in products["products"]:
            print(product["name"])
            # todo use "short_url": "https://sahil.gumroad.com/l/pencil",
    else:
        print(f"Error retrieving products: {response.status_code}")
