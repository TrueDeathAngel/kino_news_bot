import requests
from bs4 import BeautifulSoup

url = 'https://www.kinoafisha.info/releases/'


def get_releases_list():
    text = ''

    try:
        response = requests.get(url)
        text = response.text
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    soup = BeautifulSoup(text, "lxml")
    raw_film_list = soup.find_all('div', {'class': 'movieList_item'})
    film_list = [
            {
                'title':
                    film.find('a', {'class': 'movieItem_title'})
                        .text
                        .replace("'", ''),
                'genres':
                    film.find('span', {'class': 'movieItem_genres'})
                        .text
                        .replace(' ', '')
                        .split(','),
                'year':
                    film.find('span', {'class': 'movieItem_year'})
                        .text
                        .split(', ')[0]
                        .replace(' ', '')
            }
            for film in raw_film_list
        ]

    return film_list[:10]
