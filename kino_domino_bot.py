from telegram.ext import Updater, CommandHandler, MessageHandler, Filters 



def greet_user(bot, update):
	print('Вызван/ start')
	bot.sendMessage(update.message.chat_id, text='Привет, друг! Что-то мне подсказывает, что ты хочешь сходить в кино :)  Какой фильм хочешь посмотреть?')


def location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    update.message.reply_text('Спасибо')


def show_error(bot, update, error):
    print('Update "{}" caused error "{}"'.format(update, error))

def talk_to_me(bot, update):
    print("Пришло сообщение: " + update.message.text)
    bot.sendMessage(update.message.chat_id, get_answer(update.message.text, dialog))    

def main():
	updater = Updater("311306094:AAEQsNUCsvCf9gO1xEdaY_F5VLlZQ725Q1g")
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", greet_user))
	dp.add_handler(MessageHandler(Filters.location, location))
	dp.add_handler(MessageHandler([Filters.text], talk_to_me))
	dp.add_error_handler(show_error)
	updater.start_polling()
	updater.idle()
if __name__== '__main__':
    main()

