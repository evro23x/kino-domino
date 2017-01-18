from telegram.ext import Updater, CommandHandler, MessageHandler, Filters 
#from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton
#from db_quering import get_movie_id, is_on_screen, find_closest_theater, get_time_table_of_theater_by_id, parse_time_table, main_search

#markup = types.ReplyKeyboardMarkup()

def greet_user(bot, update):	
	print('Вызван/ start')
	bot.sendMessage(update.message.chat_id, text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')


def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))

def get_movie_id(user_input):
    output_query = Movies.query.filter(Movies.title.like("%"+update.message.chat_id[1:]+"%")).all()
    if len(output_query) == 1:
        return output_query[0].id
    else:
        raise UserRequestFail()

def talk_to_me(bot, update):
    print("Пришло сообщение: " + update.message.text)
    film_list = ["Неоновый демон", "Драйв", "Шерлок"]
    user_film = update.message.text

    custom_keyboard = [[ user_film]] 
    rm = ReplyKeyboardMarkup(custom_keyboard)

    if user_film in film_list:
    	bot.sendMessage(update.message.chat_id,  text='Угу, я тебя вроде понял и даже что-то нашел :) Выбери, пожалуйста, вариант фильма', reply_markup=rm)
    	
    	 

    else:
    	bot.sendMessage(update.message.chat_id, text="Не найдено")




def main():
	updater = Updater("311306094:AAEQsNUCsvCf9gO1xEdaY_F5VLlZQ725Q1g")
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", greet_user))
	#dp.add_handler(MessageHandler(Filters.location, location))
	dp.add_handler(MessageHandler([Filters.text], talk_to_me))
	dp.add_error_handler(show_error)
	updater.start_polling()
	updater.idle()
if __name__== '__main__':
    main()

