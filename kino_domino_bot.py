from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from db_quering import UserRequestFail
from db_schema import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton
from config import telegram_api_key


def greet_user(bot, update):
    print('Вызван/ start')
    bot.sendMessage(update.message.chat_id,
                    text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')


def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))


def get_movie_id(user_input):
    output_query = Movies.query.filter(Movies.title.like("%" + update.message.chat_id[1:] + "%")).all()
    if len(output_query) == 1:
        return output_query[0].id
    else:
        raise UserRequestFail()


def talk_to_me(bot, update):
    print("Пришло сообщение: " + update.message.text)
    film_list = ["Драйв", "Каро", "12:45", "400", "Арбатская"] #["Шерлок", "Синема Стар", "16:00", "300"], ["Пассажиры", "Формула Кино", "16:00", "300"]]
    user_query = update.message.text
    
    custom_keyboard = [[ user_query]] 
    rm = ReplyKeyboardMarkup(custom_keyboard)

    if user_query in film_list:
        user_film = bot.sendMessage(update.message.chat_id,  text='Угу, я тебя вроде понял и даже что-то нашел :) Уточни, пожалуйста, вариант фильма', reply_markup=rm)
        if user_film == user_query:
            user_location = bot.sendMessage(update.message.chat_id, text='Отличный выбор! Давай теперь выберем кинотеатр. Где ты сейчас находишься?')
            if user_location in film_list:
                bot.sendMessage(update.message.chat_id, film_list)  #text='Тадаам! А вот и сеансы:', film_list)
    else:
        bot.sendMessage(update.message.chat_id, text="Не найдено")


def main():
    updater = Updater(telegram_api_key)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    # dp.add_handler(MessageHandler(Filters.location, location))
    dp.add_handler(MessageHandler([Filters.text], talk_to_me))
    dp.add_error_handler(show_error)
    updater.start_polling()
    updater.idle()


# def user_location(station):
#    user_film = update.message.text
#    custom_keyboard = [[ user_film]]
#    rm = ReplyKeyboardMarkup(custom_keyboard)


# def get_user_location(latitude, longitude):
#     request location


if __name__ == '__main__':
    main()
