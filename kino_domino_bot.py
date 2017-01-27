from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler 
#from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove #InlineQueryResult
from db_quering import get_movie_id, is_on_screen, find_closest_theater2, get_movie_slots_in_theater_at_period, parse_time_table, main_search

GET_A_MOVIE_NAME, ANALYZE_USER_LOCATION = range(2)

USER_INPUT = ""
USER_LOCATION = (0.0,0.0)

def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))
    

def greet_user(bot, update): 
    print('Вызван/ start')
    bot.sendMessage(update.message.chat_id, text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')
    return  GET_A_MOVIE_NAME


def get_a_movie_name(bot, update): # может вернуть несколько id, в случае нескольких вариантов
    global USER_INPUT 
    USER_INPUT = update.message.text 
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[ location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, text="Отличный выбор! Давай теперь выберем кинотеатр?", reply_markup=reply_markup)
    return ANALYZE_USER_LOCATION



    
"""def ask_for_location(bot, update):
    location_keyboard = KeyboardButton(text="Найди кино рядом", request_location=True)
    custom_keyboard = [[ location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.sendMessage(update.message.chat_id, reply_markup=reply_markup)

    return ANALYZE_USER_LOCATION"""



def analize_user_location(bot, update):
    your_location = update.message.location
    global USER_LOCATION
    USER_LOCATION = (your_location.latitude, your_location.longitude)
    print(USER_LOCATION)
    print(USER_INPUT)
    timetable = main_search(USER_INPUT, USER_LOCATION)
    print(timetable)
    print('LOL')
    bot.sendMessage(update.message.chat_id, timetable)
    #return GIVE_A_MOVIE_LIST


    
"""def give_a_movie_list(bot, update):
    timetable = main_search(USER_INPUT, USER_LOCATION)
    print(timetable)
    bot.sendMessage(update.message.chat_id, timetable)"""



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

                #ASK_FOR_LOCATION: [MessageHandler([Filters.text], ask_for_location)],

                ANALYZE_USER_LOCATION: [MessageHandler([Filters.location], analize_user_location)],

                #GIVE_A_MOVIE_LIST: [MessageHandler([Filters.text], give_a_movie_list)],

                #GIVE_A_MOVIE_LIST: [MessageHandler([Filters.location], give_a_movie_list)]
            


        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(show_error)
    updater.start_polling()
    updater.idle()
if __name__== '__main__':
    main()


