import requests
from bs4 import BeautifulSoup

import db_handler
from db_handler import get_random_movie_by_genre, add_movies, get_movie_year

db_handler.get_movie_genres_list('a', db_handler.series_genres_table_name)
db_handler.get_movie_year('a', db_handler.series_years_table_name)

url = 'https://www.kinoafisha.info/rating/series/?page='
for i in range(0, 7):
    text = ''

    try:
        response = requests.get(url+str(i))
        text = response.text
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    soup = BeautifulSoup(text, "lxml")
    print(i)
    raw_film_list = soup.find_all('div', {'class': 'movieItem_info'})
    film_list = [
        {
            'title':
                film.find(('a', {'class': 'movieItem_title'}))
                    .text
                    .replace("'", ''),
            'genres':
                film.find(('div', {'class': 'movieItem_details'}))
                    .find(('span', {'class': 'movieItem_genres'}))
                    .text
                    .replace(' ', '')
                    .split(','),
            'year':
                film.find(('div', {'class': 'movieItem_details'}))
                    .find_all(('span', {'class': 'movieItem_year'}))[-1]
                    .text
                    .split(', ')[0]
                    .replace(' ', '')
        }
        for film in raw_film_list
    ]
    for film in film_list:
        print(film)

    add_movies(film_list, db_handler.series_genres_table_name, db_handler.series_years_table_name)
