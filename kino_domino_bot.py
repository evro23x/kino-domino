from telegram.ext import Updater, CommandHandler, MessageHandler, Filters 
#from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton #InlineQueryResult
#from db_quering import main_search, get_movie_id, is_on_screen, find_closest_theater, get_time_table_of_theater_by_id, parse_time_table

def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))

def greet_user(bot, update):
    print('Вызван/ start')
    bot.sendMessage(update.message.chat_id, text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')


def get_location(bot, update):
    #print("гео работает")
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[ location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text="Отличный выбор! Давай теперь выберем кинотеатр?", reply_markup=reply_markup)

def get_movie(bot, update): 
    film_list = ["Драйв", "Молчание ягнят", "Гарри Поттер", "300 спартанцев", "Дети арбата"]
    new_film_list = []
    user_query = update.message.text
    for film in film_list:
        if user_query in film:
            new_film_list.append([film])
    custom_keyboard = new_film_list
    rm = ReplyKeyboardMarkup(custom_keyboard)

    if len(new_film_list) > 0:
        bot.sendMessage(update.message.chat_id, text='Угу, я тебя вроде понял и даже что-то нашел :) Уточни, пожалуйста, вариант фильма', reply_markup=rm
        )                    
    else:
        bot.sendMessage(update.message.chat_id, text="Не найдено")
    
    if update.message.text in film_list:
        get_location(bot, update)



def main():
    updater = Updater("311306094:AAEQsNUCsvCf9gO1xEdaY_F5VLlZQ725Q1g")
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    #dp.add_handler(MessageHandler([Filters.text], talk_to_me))

    dp.add_handler(MessageHandler([Filters.text], get_movie))
    #dp.add_handler(MessageHandler([Filters.text], get_location))
    #dp.add_handler(MessageHandler([Filters.text], get_location))



    dp.add_error_handler(show_error)
    updater.start_polling()
    updater.idle()
if __name__== '__main__':
    main()

