from threading import Thread
from time import sleep, time
try:
    import telebot
    from telebot import types
except ModuleNotFoundError:
    import os
    os.system('pip install pyTelegramBotAPI')
    import telebot
    from telebot import types

class UserData:
    def __init__(self, username: str):
        self.username = username
    username: str

    reported_messages: list = []
    reported_by: list = []
    reports: int = 0

user_datas = []

def find_user_data_index(username: str) -> int:
    for index in range(0, len(user_datas)):
        if user_datas[index].username == username:
            return index
    return -1  

def handle_user(func):
    def wrapper(message):
        if find_user_data_index(message.from_user.username) == -1:
            user_datas.append(UserData(message.from_user.username))
            print(f'Новый пользователь {message.from_user.username} может быть взаимодействован через бота')
        func(message)
    return wrapper

if __name__ == '__main__':
    bot = telebot.TeleBot('yourtokenhere')

    # отвечает на команду, а через некоторое время удаляет ответ и команду (чтобы не засорять чат)
    def reply_and_delete(message: types.Message, text: str):
        def reply_and_delete_thread():
            nonlocal message, text
            bot_message = bot.reply_to(message, text)
            sleep(10)
            bot.delete_message(bot_message.chat.id, bot_message.id)
            bot.delete_message(bot_message.reply_to_message.chat.id, bot_message.reply_to_message.id)
        Thread(target=reply_and_delete_thread()).start()

    @bot.message_handler(commands=['report'])
    @handle_user
    def report(message: types.Message):
        if message.reply_to_message == None:
            reply_and_delete(message, 'Должно быть ответом на сообщение!')
        elif message.reply_to_message.from_user.username == message.from_user.username or message.reply_to_message.from_user.is_bot:
            reply_and_delete(message, 'Хватит дурачиться.')
        else:
            try:
                user_index = find_user_data_index(message.reply_to_message.from_user.username)
                if not user_datas[user_index].reported_by.__contains__(message.from_user.username):
                    user_datas[user_index].reports += 1
                    user_datas[user_index].reported_messages.append(message.reply_to_message)
                    user_datas[user_index].reported_by.append(message.from_user.username)
                    reply_and_delete(message, 'Репорт отправлен')
                    if user_datas[user_index].reports >= 2:
                        bot.restrict_chat_member(message.chat.id, message.reply_to_message.from_user.id, until_date=time()+100)
                        
                        for rep_message in user_datas[user_index].reported_messages:
                            try:
                                bot.delete_message(rep_message.chat.id, rep_message.id)
                            except:
                                continue

                        user_datas[user_index].reports = 0
                        user_datas[user_index].reported_messages = []
                        user_datas[user_index].reported_by = []
                else:
                    reply_and_delete(message, 'Вы уже отправляли репорт на этого пользователя')
            except:
                reply_and_delete(message, 'Не удалось отправить репорт.')
 
    @bot.message_handler(commands=['ban'])
    @handle_user
    def ban(message: types.Message):
        status = bot.get_chat_member(message.chat.id, message.from_user.id).status
        if message.reply_to_message == None:
            reply_and_delete(message, 'Должна быть ответом на сообщение!')
        elif status != 'creator' and status != 'administrator':
            reply_and_delete(message, 'Недостаточно прав!')
        else:
            try:
                bot.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
                reply_and_delete(message, 'Участник успешно забанен!')
            except:
                reply_and_delete(message, 'Не удалось забанить участника.')

    @bot.message_handler()
    @handle_user
    def message_handling(message: types.Message):
        pass

    bot.polling(True)