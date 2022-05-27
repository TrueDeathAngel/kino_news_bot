import telebot
from info import TOKEN
from db_handler import get_selected_genres_list, remove_genre, add_genre

# Создаем экземпляр бота
bot = telebot.TeleBot(TOKEN)

genres_set = {'анимация', 'аниме', 'балет', 'биография', 'боевик', 'вестерн', 'военный', 'детектив',
              'детский', 'документальный', 'драма', 'исторический', 'комедия', 'концерт', 'короткометражный',
              'криминал', 'мелодрама', 'мистика', 'музыка', 'мюзикл', 'приключения', 'сборник', 'семейный',
              'сказка', 'спорт', 'триллер', 'ужасы', 'фантастика', 'фэнтези', 'эротика'}


# genre keyboard
def get_genre_update_keyboard(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    for genre in genres_set:
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                '✅' + genre[1] if genre[0] in get_selected_genres_list(chat_id) else genre[1],
                callback_data=genre[0]
            )
        )

    return keyboard


# news
def news(message):
    bot.send_message(message.chat.id, 'NEWS')


# random_film
def random_film(message):
    bot.send_message(message.chat.id, 'RANDOM_FILM')


# random_series
def random_series(message):
    bot.send_message(message.chat.id, 'RANDOM_SERIES')


# Меню выбора жанра
def genres(message):
    bot.send_message(
        message.chat.id, 'Вы можете выбрать предпочитаемые жанры из списка. '
                         'Они будут использоваться для поиска подходящего вам контента:',
        reply_markup=get_genre_update_keyboard(message.chat.id)
    )


# info
def info(message):
    bot.send_message(message.chat.id, 'INFO')


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
    if query.data in genres_set:
        bot.answer_callback_query(query.id)  # убираем состоянме загрузки
        if query.data in get_selected_genres_list(query.message.chat.id):
            remove_genre(query.message.chat.id, query.data)
        else:
            add_genre(query.message.chat.id, query.data)
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
