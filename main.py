try:
    import telebot
    from telebot import types
except ModuleNotFoundError:
    import os
    os.system('pip install pyTelegramBotAPI')
    import telebot
    from telebot import types

# Handles all user local data. Define here all local variables you need.
class UserData:
    def __init__(self, username: str):
        self.username = username
    username: str
    # Determinate what's user want type in text linker
    # Example: if user wants to create post, he will type /post (it's @message_handler(commands=['post'])) which should set his text_type to 'post_create'
    # Then he types text that describes his post, it's text_linker: ... elif user_datas[user_index]: ...
    # By default it's 'start', which executes if user_datas[user_index] == 'start'
    text_type: str = "start"

# Handles local data of all users (UserData)
user_datas = []

# Finds user_data in user_datas by username, returns normal index or -1 if user not found.
def find_user_data_index(username: str) -> int:
    for index in range(0, len(user_datas)):
        if user_datas[index].username == username:
            return index
    return -1  

# Checkes if user in user_datas, if not then it adds user and reports it. Use for all functions that use user's data.
# Also use it after @message_handler. Your code must look like this:
# @bot.message_handler(commands=['some_command'])
# @handle_user
# def some_command_implementation():
def handle_user(func):
    def wrapper(message):
        if find_user_data_index(message.from_user.username) == -1:
            user_datas.append(UserData(message.from_user.username))
            print(f'New user {message.from_user.username} started talking to a bot')
        func(message)
    return wrapper


if __name__ == '__main__':
    # example code

    bot = telebot.TeleBot('yourtokenhere')

    @bot.message_handler(commands=['start', 'help'])
    @handle_user
    def start(message: types.Message):
        user_datas[find_user_data_index(message.from_user.username)].text_type = 'start'
        bot.send_message(message.chat.id, f'Nice to see you, {message.from_user.username}')

    # can be deleted when used on practice
    @bot.message_handler(commands=['echo'])
    @handle_user
    def echo(message: types.Message):
        bot.send_message(message.chat.id, f'Type me something and i will answer same, or type /start to exit')
        user_datas[find_user_data_index(message.from_user.username)].text_type = 'echo'

    @bot.message_handler()
    @handle_user
    def input_linker(message: types.Message):
        user_index = find_user_data_index(message.from_user.username)
        if user_datas[user_index].text_type == 'start' or message.text == 'Back':
            start(message)
        # can be deleted when used on practice
        elif user_datas[user_index].text_type == 'echo':
            bot.send_message(message.chat.id, message.text)
        else:
            bot.send_message(message.chat.id, "Didn't understood you.")

    bot.polling()