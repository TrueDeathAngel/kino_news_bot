import telebot
from info import TOKEN
import db_handler as db
from releases import get_releases_list

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)


# genre keyboard
def get_genre_update_keyboard(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for genre in db.genres_set:
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                '✅' + genre if genre in db.get_selected_genres_list(chat_id) else genre,
                callback_data=genre
            )
        )
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            '🗑️Сбросить жанры🗑️',
            callback_data='reset_genres'
        )
    )

    return keyboard


# news
def news(message):
    releases_list = get_releases_list()
    result = 'Премьеры фильмов в кинотеатрах России:'
    for i, film in enumerate(releases_list):
        result += f"\n{i+1}. {film['title']} ({film['year']})" \
                  f"\n({', '.join(film['genres'])})"
    bot.send_message(message.chat.id, result)


def random_movie(message, genres_table_name, years_table_name):
    film = db.get_random_movie_by_genre(db.get_selected_genres_list(message.chat.id), genres_table_name)
    bot.send_message(message.chat.id, 'Как насчёт...\n'
                                      f'"{film}" ({db.get_movie_year(film, years_table_name)})\nЖанры: ' +
                     ', '.join(db.get_movie_genres_list(film, genres_table_name))
                     if film else 'Простите! Я не могу ничего порекомендовать. Попробуйте выбрать другие жанры')


# Рекомендуем случайный фильм, исходя из выбранных жанров
def random_film(message):
    random_movie(message, db.movies_genres_table_name, db.movies_years_table_name)


# random_series
def random_series(message):
    random_movie(message, db.series_genres_table_name, db.series_years_table_name)


# Меню выбора жанра
def genres(message):
    bot.send_message(
        message.chat.id, 'Вы можете выбрать предпочитаемые жанры из списка. '
                         'Они будут использоваться для поиска подходящего вам контента:',
        reply_markup=get_genre_update_keyboard(message.chat.id)
    )


# info
def info(message):
    bot.send_message(message.chat.id,
                     'Чтобы вам порекомендовали случайный фильм / сериал, просто нажмите на соответствующие кнопки во '
                     'всплывающем меню!\nВы также можете сделать рекомендации точнее, указав список предпочитаемых'
                     ' жанров (вы, конечно, можете выбрать там столько жанров, сколько захотите, '
                     'но лучше ограничьтесь двумя-тремя. Так больше шансов найти что-то интересное). Для этого '
                     'просто нажмите на «Жанры 💎!»')


menu = {'news': 'Что нового 🔎', 'random_film': 'Случайный фильм 🍿',
        'random_series': 'Случайный сериал 📺', 'genres': 'Жанры 💎',
        'info': 'Инструкция 📖'}

menu_functions = {menu['news']: news, menu['random_film']: random_film,
                  menu['random_series']: random_series, menu['genres']: genres,
                  menu['info']: info}


# Изменение отображаемого списка выбранных жанров
def edit_genres_keyboard(query):
    if query.message:
        bot.edit_message_reply_markup(
            query.message.chat.id,
            query.message.message_id,
            reply_markup=get_genre_update_keyboard(query.message.chat.id)
        )
    elif query.inline_message_id:
        bot.edit_message_reply_markup(
            inline_message_id=query.inline_message_id,
            reply_markup=get_genre_update_keyboard(query.message.chat.id)
        )


@bot.callback_query_handler(func=lambda call: True)
def callback(query):
    if query.data in db.genres_set:
        bot.answer_callback_query(query.id)  # убираем состоянме загрузки
        if query.data in db.get_selected_genres_list(query.message.chat.id):
            db.remove_genre(query.message.chat.id, query.data)
        else:
            db.add_genre(query.message.chat.id, query.data)
        edit_genres_keyboard(query)
    elif query.data == 'reset_genres':
        db.reset_genres(query.message.chat.id)
        edit_genres_keyboard(query)


# Функция, обрабатывающая команду /start
@bot.message_handler(commands=["start"])
def start(message):
    reply_keyboard = telebot.types.ReplyKeyboardMarkup()
    reply_keyboard.row(
        telebot.types.KeyboardButton(menu['news'])
    )
    reply_keyboard.row(
        telebot.types.KeyboardButton(menu['random_film']),
        telebot.types.KeyboardButton(menu['random_series'])
    )
    reply_keyboard.row(
        telebot.types.KeyboardButton(menu['genres'])
    )
    reply_keyboard.row(
        telebot.types.KeyboardButton(menu['info'])
    )
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!', reply_markup=reply_keyboard)


# Функция, взаимодействующая с вводимым текстом
@bot.message_handler(content_types='text')
def text_handler(message):
    if message.text in menu.values():
        try:
            menu_functions[message.text](message)
        except Exception as ex:
            print(ex)


# Запускаем бота
bot.polling(none_stop=True, interval=1)
