from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler 
#from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove #InlineQueryResult
#from db_quering import main_search, get_movie_id, is_on_screen, find_closest_theater, get_time_table_of_theater_by_id, parse_time_table

GET_A_MOVIE_NAME, ASK_FOR_LOCATION, ANALYZE_USER_LOCATION = range(3)

def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))
    

def greet_user(bot, update):
    print('Вызван/ start')
    bot.sendMessage(update.message.chat_id, text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')
    return  GET_A_MOVIE_NAME


def get_a_movie_name(bot, update): 
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
        return ASK_FOR_LOCATION
    else:
        bot.sendMessage(update.message.chat_id, text="Не найдено. Уточни запрос")
        return GET_A_MOVIE_NAME



    
def ask_for_location(bot, update):
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[ location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text="Отличный выбор! Давай теперь выберем кинотеатр?", reply_markup=reply_markup)

    return ANALYZE_USER_LOCATION



def analize_user_location(bot, update):
    session_list = ["Драйв", "Каро", "13:15", "400"] #55.78807, 37.609866]
    user_location = update.message.location
    your_location = [user_location.latitude, user_location.longitude]
    print(your_location)
    bot.sendMessage(update.message.chat_id, text="Тадаам! А вот и сеансы:")



"""movie_id = get_movie_id(update.message.text)
closest_theater = find_closest_theater(user_coordinates, movie_id)# user_coordinates - кортеж (latitude, longitude)"""


def cancel(bot, update):
    bot.sendMessage(update.message.chat_id,'Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    updater = Updater("311306094:AAEQsNUCsvCf9gO1xEdaY_F5VLlZQ725Q1g")
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', greet_user)],


        states={ 
                 
                GET_A_MOVIE_NAME: [MessageHandler([Filters.text], get_a_movie_name)],

                ASK_FOR_LOCATION: [MessageHandler([Filters.text], ask_for_location)],

                ANALYZE_USER_LOCATION: [MessageHandler([Filters.location], analize_user_location)]
            


        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(show_error)
    updater.start_polling()
    updater.idle()
if __name__== '__main__':
    main()



