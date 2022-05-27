import sqlite3

users_selected_genres_table_name = 'users_selected_genres'
movies_genres_table_name = 'movies_genres'
movies_years_table_name = 'movies_years'
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


def get_movie_list(genre):
    movie_list = []
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT movie FROM {movies_genres_table_name} WHERE genre = '{genre}'")
        movie_list = [item[0] for item in cursor.fetchall()]
    except sqlite3.OperationalError:
        cursor.execute(f'''CREATE TABLE {movies_genres_table_name}
                    (
                    movie VARCHAR(100),
                    genre VARCHAR(50)
                    )''')

    cursor.close()

    return movie_list


def get_movie_year(movie):
    year = ''
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT year FROM {movies_years_table_name} WHERE movie = '{movie}'")
        year = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        cursor.execute(f'''CREATE TABLE {movies_years_table_name}
                    (
                    movie VARCHAR(100),
                    year VARCHAR(5)
                    )''')

    cursor.close()

    return year


def add_movies(movie_list):
    for movie in movie_list:
        for genre in movie['genres']:
            update_database(f"INSERT INTO {movies_genres_table_name}" +
                            "(movie, genre) VALUES ('{0}', '{1}')".format(movie['title'].replace("'", ''), genre))
        update_database(f"INSERT INTO {movies_years_table_name}" +
                        "(movie, year) VALUES ('{0}', {1})".format(movie['title'].replace("'", ''), movie['year']))
