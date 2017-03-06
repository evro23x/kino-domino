from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
# from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove  # InlineQueryResult
from db_quering import get_current_movie_id, find_closest_theater, get_movie_slots_in_theater_at_period, \
    parse_time_table, main_search
from request_movie_db import get_movie_id, find_similar_movie
import config

GET_A_MOVIE_NAME, ANALYZE_USER_LOCATION, WHAT_TO_DO_NEXT, GET_A_SIMILAR_MOVIE = range(4)

USER_INPUT = {}
USER_LOCATION = {}

FINAL_PHRASE = "Для возобновления диалога нажми /start"


def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))


def greet_user(bot, update):
    print('Вызван/ start')
    variants = [['Посмотреть кино дома'], ['Сходить в кино']]
    custom_keyboard = variants
    rm = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text="Привет, друг! Чего бы тебе хотелось?", reply_markup=rm)
    return WHAT_TO_DO_NEXT


def what_to_do_next(bot, update):
    user_choice = [update.message.text]
    variants = [['Посмотреть кино дома'], ['Сходить в кино']]
    if user_choice == variants[1]:
        bot.sendMessage(update.message.chat_id, text="Хорошо! Какой фильм хочешь посмотреть?",
                        reply_markup=ReplyKeyboardRemove())
        return GET_A_MOVIE_NAME
    else:
        bot.sendMessage(update.message.chat_id,
                        text="Здорово! Знаешь, у меня хороший вкус, да и фильмов я много пересмотрел, так что могу "
                             "тебе подсказать. Назови мне фильм, а я тебе порекомендую похожие.",
                        reply_markup=ReplyKeyboardRemove())
        return GET_A_SIMILAR_MOVIE


def get_a_similar_movie(bot, update):
    # chat_id = update.message.chat_id
    movie_id = get_movie_id(update.message.text)
    print(movie_id)
    not_found_error_msg = "Извини, но я не слышал о таком фильме. Назови какой-нибудь другой фильм,я попробую еще раз."
    if movie_id is None:
        bot.sendMessage(update.message.chat_id,
                        text=not_found_error_msg)
        return GET_A_SIMILAR_MOVIE

    similar_movie_title = find_similar_movie(movie_id)
    if similar_movie_title is None:
        bot.sendMessage(update.message.chat_id,
                        text=not_found_error_msg)
        return GET_A_SIMILAR_MOVIE
    else:
        bot_phrase = "Да, это хороший фильм! Если тебе он и правда нравится, то ты наверняка оценишь это: "\
                     + similar_movie_title + '\nНажми /cancel, чтобы закончить.'
        bot.sendMessage(update.message.chat_id, bot_phrase)


def get_a_movie_name(bot, update):
    global USER_INPUT
    chat_id = update.message.chat_id
    USER_INPUT[chat_id] = update.message.text
    movie_id = get_current_movie_id(update.message.text)
    if movie_id is None:
        bot.sendMessage(update.message.chat_id,
                        text="Извини, но этот фильм сейчас не идет в кинотеатрах. Попробуй еще раз.")
        return GET_A_MOVIE_NAME

    print(USER_INPUT)
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text="Отличный выбор! Давай теперь выберем кинотеатр?",
                    reply_markup=reply_markup)
    return ANALYZE_USER_LOCATION


def analyze_user_location(bot, update):
    chat_id = update.message.chat_id
    global USER_LOCATION
    USER_LOCATION[chat_id] = (update.message.location.latitude, update.message.location.longitude)
    print(USER_LOCATION)
    print(USER_INPUT)
    timetable = main_search(USER_INPUT[chat_id], USER_LOCATION[chat_id])
    print(timetable)
    final_phrase = timetable + 'Нажми /cancel, чтобы закончить.'
    bot.sendMessage(update.message.chat_id, final_phrase, reply_markup=ReplyKeyboardRemove())


def cancel(bot, update):
    bot.sendMessage(update.message.chat_id, 'Пока! Надеюсь, я помог тебе! \n' + FINAL_PHRASE,
                    reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    updater = Updater(config.telegram_api_key)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', greet_user)],

        states={
            GET_A_MOVIE_NAME: [MessageHandler([Filters.text], get_a_movie_name)],
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
