from telegram.ext import Updater, CommandHandler, MessageHandler, Filters 
from db import db_session, MovieTheaters, MetroStations, TimeSlots, Movies, MovieFormats
from telegram import ReplyKeyboardMarkup, KeyboardButton

#markup = types.ReplyKeyboardMarkup()

def greet_user(bot, update):	
	print('Вызван/ start')
	bot.sendMessage(update.message.chat_id, text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')


def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))

def talk_to_me(bot, update):
    print("Пришло сообщение: " + update.message.text)
    film_list = ["Неоновый носочек", "Драйв", "Шерлок"]
    user_film = update.message.text

    custom_keyboard = [[ user_film]] #['2'], ['3'], ['4']]
    rm = ReplyKeyboardMarkup(custom_keyboard)

    if user_film in film_list:
    	bot.sendMessage(update.message.chat_id,  text='Угу, я тебя вроде понял и даже что-то нашел :) Выбери, пожалуйста, вариант фильма', reply_markup=rm)
    	 

    else:
    	bot.sendMessage(update.message.chat_id, text="Не найдено")


#def location(bot, update):
 #   user = update.message.from_user
  #  user_location = update.message.location
   # update.message.reply_text('')



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

