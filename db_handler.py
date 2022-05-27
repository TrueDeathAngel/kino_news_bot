import sqlite3

table_name = 'users_selected_genres'
database_name = 'bot_users.db'


def get_selected_genres_list(chat_id):
    genres_list = []
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT genre FROM {table_name} WHERE chat_id = {chat_id}")
        genres_list = [item[0] for item in cursor.fetchall()]
    except sqlite3.OperationalError:
        cursor.execute(f'''CREATE TABLE {table_name}
                    (
                    chat_id INT,
                    genre VARCHAR(50)
                    )''')

    cursor.close()

    return genres_list


def update_table(command):
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
    update_table(f"DELETE FROM {table_name} WHERE chat_id = {chat_id} AND genre = '{genre}'")


def add_genre(chat_id, genre):
    update_table(f"INSERT INTO {table_name} (chat_id, genre) VALUES ({chat_id}, '{genre}')")
