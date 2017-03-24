from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
# from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove  # InlineQueryResult
from db_quering import get_current_movie_id, main_search, get_theater_by_name
from request_movie_db import get_movie_id, find_similar_movie
from config import tmdb_api_key_for_bot, telegram_api_key
from datetime import datetime, date, timedelta
from sql_wrapper import add_log, get_premier_dict

GET_A_MOVIE_NAME, ANALYZE_USER_LOCATION, WHAT_TO_DO_NEXT, GET_A_SIMILAR_MOVIE, GET_A_CINEMA_CHOOSE, GET_A_CINEMA_NAME \
    = range(6)

USER_INPUT = {}
USER_LOCATION = {}

FINAL_PHRASE = "Для возобновления диалога нажми /start"


def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))


def greet_user(bot, update):
    rm = ReplyKeyboardMarkup([['Посмотреть кино дома'], ['Сходить в кинотеатр']])
    bot.sendMessage(update.message.chat_id, text="Привет, друг! Чего бы тебе хотелось?", reply_markup=rm)
    add_log(update, msg_in='/start', msg_out='')
    return WHAT_TO_DO_NEXT


def what_to_do_next(bot, update):
    variants = [['Посмотреть кино дома'], ['Сходить в кинотеатр']]
    if [update.message.text] == variants[1]:
        rm = ReplyKeyboardMarkup([['По названию фильма'], ['По названию кинотеатра'], ['Премьеры']])
        bot.sendMessage(update.message.chat_id, text="Выбери, по каким критериям будем искать фильм?", reply_markup=rm)
        return GET_A_CINEMA_CHOOSE
    else:
        bot.sendMessage(update.message.chat_id,
                        text="Здорово! Знаешь, у меня хороший вкус, да и фильмов я много пересмотрел, так что могу "
                             "тебе подсказать. Назови мне фильм, а я тебе порекомендую похожие.",
                        reply_markup=ReplyKeyboardRemove())
        add_log(update, msg_in='"Посмотреть кино дома"', msg_out='')
        return GET_A_SIMILAR_MOVIE


def get_a_cinema_choose(bot, update):
    variants = [['По названию фильма'], ['По названию кинотеатра'], ['Премьеры']]
    if [update.message.text] == variants[0]:
        bot.sendMessage(update.message.chat_id, text="Хорошо! Какой фильм хочешь посмотреть?",
                        reply_markup=ReplyKeyboardRemove())
        add_log(update, msg_in='По названию фильма', msg_out='')
        return GET_A_MOVIE_NAME
    elif [update.message.text] == variants[1]:
        bot.sendMessage(update.message.chat_id, text="Хорошо! Как называется кинотеатр?",
                        reply_markup=ReplyKeyboardRemove())
        add_log(update, msg_in='По названию кинотеатра', msg_out='')
        return GET_A_CINEMA_NAME

    else:
        movies_dict = get_premier_dict()
        premier_info = "Премьеры недели:\n\n"
        for movie_obj in movies_dict:
            premier_info += movie_obj.title
            premier_info += " - <a href='" + movie_obj.trailer_url + "'>трейлер</a>\n"
        bot.sendMessage(update.message.chat_id, text=premier_info, parse_mode='HTML')
        return greet_user(bot, update)


def get_a_similar_movie(bot, update):
    movie_id = get_movie_id(update.message.text)
    add_log(update, msg_in='Название фильма = ' + str(update.message.text), msg_out='')
    not_found_error_msg = "Извини, но я не слышал о таком фильме. Назови какой-нибудь другой фильм,я попробую еще раз."
    if movie_id is None:
        bot.sendMessage(update.message.chat_id, text=not_found_error_msg)
        add_log(update, msg_in='', msg_out=not_found_error_msg)
        return GET_A_SIMILAR_MOVIE

    similar_movie_title = find_similar_movie(movie_id)
    if similar_movie_title is None:
        bot.sendMessage(update.message.chat_id, text=not_found_error_msg)
        add_log(update, msg_in='', msg_out=not_found_error_msg)
        return GET_A_SIMILAR_MOVIE
    else:
        bot_phrase = "Да, это хороший фильм! Если тебе он и правда нравится, то ты наверняка оценишь это: " \
                     + similar_movie_title + '\nНажми /cancel, чтобы закончить.'
        bot.sendMessage(update.message.chat_id, bot_phrase)
        add_log(update, msg_in='', msg_out=bot_phrase)


def get_a_cinema_name(bot, update):
    global USER_INPUT
    chat_id = update.message.chat_id
    USER_INPUT[chat_id] = update.message.text
    theater = get_theater_by_name(update.message.text)
    print(theater.id)
    exit(0)
    add_log(update, msg_in='Название фильма = ' + str(update.message.text), msg_out='')
    not_found_error_msg = "Извини, но этот фильм сейчас не идет в кинотеатрах. Попробуй еще раз."
    if movie_id is None:
        bot.sendMessage(chat_id, text=not_found_error_msg)
        add_log(update, msg_in='', msg_out=not_found_error_msg)
        return GET_A_MOVIE_NAME
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    find_movie_success = "Отличный выбор! Давай теперь выберем кинотеатр?"
    bot.sendMessage(chat_id, text=find_movie_success, reply_markup=reply_markup)
    add_log(update, msg_in="", msg_out=find_movie_success)
    return ANALYZE_USER_LOCATION


def get_a_movie_name(bot, update):
    global USER_INPUT
    chat_id = update.message.chat_id
    USER_INPUT[chat_id] = update.message.text
    movie_id = get_current_movie_id(update.message.text)
    add_log(update, msg_in='Название фильма = ' + str(update.message.text), msg_out='')
    not_found_error_msg = "Извини, но этот фильм сейчас не идет в кинотеатрах. Попробуй еще раз."
    if movie_id is None:
        bot.sendMessage(chat_id, text=not_found_error_msg)
        add_log(update, msg_in='', msg_out=not_found_error_msg)
        return GET_A_MOVIE_NAME
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    find_movie_success = "Отличный выбор! Давай теперь выберем кинотеатр?"
    bot.sendMessage(chat_id, text=find_movie_success, reply_markup=reply_markup)
    add_log(update, msg_in="", msg_out=find_movie_success)
    return ANALYZE_USER_LOCATION


def analyze_user_location(bot, update):
    chat_id = update.message.chat_id
    global USER_LOCATION
    USER_LOCATION[chat_id] = (update.message.location.latitude, update.message.location.longitude)
    add_log(update, msg_in=str(update.message.location.latitude) + " " + str(update.message.location.longitude),
            msg_out='')
    timetable = main_search(USER_INPUT[chat_id], USER_LOCATION[chat_id])
    # add_log(update, msg_in="", msg_out=timetable)
    add_log(update, msg_in="", msg_out="Результат отправлен пользователю")
    final_phrase = timetable + '\nНажми /cancel, чтобы закончить.'
    bot.sendMessage(update.message.chat_id, final_phrase, reply_markup=ReplyKeyboardRemove())


def cancel(bot, update):
    goodbye_phrase = 'Пока! Надеюсь, я помог тебе! \n' + FINAL_PHRASE
    bot.sendMessage(update.message.chat_id, goodbye_phrase, reply_markup=ReplyKeyboardRemove())
    add_log(update, msg_in='/cancel', msg_out='')

    return ConversationHandler.END


def main():
    updater = Updater(telegram_api_key)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', greet_user)],

        states={
            GET_A_MOVIE_NAME: [MessageHandler([Filters.text], get_a_movie_name)],
            GET_A_CINEMA_NAME: [MessageHandler([Filters.text], get_a_cinema_name)],
            GET_A_CINEMA_CHOOSE: [MessageHandler([Filters.text], get_a_cinema_choose)],
            ANALYZE_USER_LOCATION: [MessageHandler([Filters.location], analyze_user_location)],
            WHAT_TO_DO_NEXT: [MessageHandler([Filters.text], what_to_do_next)],
            GET_A_SIMILAR_MOVIE: [MessageHandler([Filters.text], get_a_similar_movie)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(show_error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
