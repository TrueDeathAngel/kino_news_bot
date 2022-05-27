import sqlite3


genres_set = {'анимация', 'аниме', 'балет', 'биография', 'боевик', 'вестерн', 'военный', 'детектив',
              'детский', 'документальный', 'драма', 'исторический', 'комедия', 'концерт', 'короткометражный',
              'криминал', 'мелодрама', 'мистика', 'музыка', 'мюзикл', 'приключения', 'сборник', 'семейный',
              'сказка', 'спорт', 'триллер', 'ужасы', 'фантастика', 'фэнтези', 'эротика'}

users_selected_genres_table_name = 'users_selected_genres'
movies_genres_table_name = 'movies_genres'
movies_years_table_name = 'movies_years'
series_genres_table_name = 'series_genres'
series_years_table_name = 'series_years'
database_name = 'bot_users.db'


def get_selected_genres_list(chat_id):
    genres_list = []
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT genre FROM {users_selected_genres_table_name} WHERE chat_id = {chat_id}")
        genres_list = [item[0] for item in cursor.fetchall()]
    except sqlite3.OperationalError:
        cursor.execute(f'''CREATE TABLE {users_selected_genres_table_name}
                    (
                    chat_id INT,
                    genre VARCHAR(50)
                    )''')

    cursor.close()

    return genres_list


def update_database(command):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()

    try:
        cursor.execute(command)
    except sqlite3.DatabaseError as err:
        print("Error: ", err)
    else:
        connection.commit()

    cursor.close()


def remove_genre(chat_id, genre):
    update_database(f"DELETE FROM {users_selected_genres_table_name} WHERE chat_id = {chat_id} AND genre = '{genre}'")


def add_genre(chat_id, genre):
    update_database(f"INSERT INTO {users_selected_genres_table_name} (chat_id, genre) VALUES ({chat_id}, '{genre}')")


def reset_genres(chat_id):
    for genre in genres_set:
        remove_genre(chat_id, genre)


# Отправляем один фильм или сериал, исходя из выбранных жанров.
# Если количество выбранных жанров равно 0, то фильм выбирается без привязки к жанру.
# Конструкция позволяет увеличивать количество жанров до бесконечности.
# Если есть подходящий фильм, то он будет найден
def get_random_movie_by_genre(genres_list, table_name):
    movie = ''
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    command = ''
    for i, genre in enumerate(genres_list[1:]):
        command += f'''\nINNER JOIN (SELECT DISTINCT movie FROM {table_name}
        WHERE genre = '{genre}') t{i+2}
            ON t1.movie = t{i+2}.movie'''
    if genres_list:
        command += f"\nWHERE genre = '{genres_list[0]}'"
    try:
        cursor.execute(f"SELECT DISTINCT t1.movie FROM {table_name} t1" + command + f"\nORDER BY RANDOM() LIMIT 1")
        movie = cursor.fetchone()[0]
    except sqlite3.OperationalError as err:
        print(err)
        cursor.execute(f'''CREATE TABLE {table_name}
                    (
                    movie VARCHAR(100),
                    genre VARCHAR(50)
                    )''')
    finally:
        cursor.close()

        return movie


def get_movie_year(movie, table_name):
    year = ''
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT year FROM {table_name} WHERE movie = '{movie}'")
        year = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        cursor.execute(f'''CREATE TABLE {table_name}
                    (
                    movie VARCHAR(100),
                    year VARCHAR(5)
                    )''')

    cursor.close()

    return year


def add_movies(movie_list, genres_table_name, years_table_name):
    for movie in movie_list:
        for genre in movie['genres']:
            update_database(f"INSERT INTO {genres_table_name} " +
                            f"(movie, genre) VALUES ('{movie['title']}', '{genre}')")
        update_database(f"INSERT INTO {years_table_name} " +
                        f"(movie, year) VALUES ('{movie['title']}', {movie['year']})")


def get_movie_genres_list(movie, table_name):
    genres_list = []
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT genre FROM {table_name} "
                       f"WHERE movie = '{movie}'")
        genres_list = [item[0] for item in cursor.fetchall()]
    except sqlite3.OperationalError:
        cursor.execute(f'''CREATE TABLE {table_name}
                    (
                    movie VARCHAR(100),
                    genre VARCHAR(50)
                    )''')

    return genres_list
