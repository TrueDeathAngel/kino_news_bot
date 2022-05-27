import requests
from bs4 import BeautifulSoup
from db_handler import get_movie_list, add_movies, get_movie_year

url = 'https://www.kinoafisha.info/rating/movies/'
text = ''

try:
    response = requests.get(url)
    text = response.text
except requests.HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')

soup = BeautifulSoup(text, "lxml")
print(len(soup))
raw_film_list = soup.find_all('div', {'class': 'movieItem_info'})
film_list = [
    {
        'title':
            film.find(('a', {'class': 'movieItem_title'}))
                .text,
        'genres':
            film.find(('div', {'class': 'movieItem_details'}))
                .find(('span', {'class': 'movieItem_genres'}))
                .text
                .split(', '),
        'year':
            film.find(('div', {'class': 'movieItem_details'}))
                .find_all(('span', {'class': 'movieItem_year'}))[-1]
                .text
                .split(', ')[0]
    }
    for film in raw_film_list
]
for film in film_list:
    print(film)

add_movies(film_list)
