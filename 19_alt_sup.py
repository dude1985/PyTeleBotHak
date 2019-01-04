
import telebot
from telebot import types
import time
import os

TELEGRAM_TOKEN = '720633788:AAHDpsGunfmCy5gzMSp40zgwoThIdK0c-LY'
path2Rootdir = 'C:\\Users\\S2\\Google Диск\\bot_data\\'

bot = telebot.TeleBot(TELEGRAM_TOKEN,threaded=False)
# создадим словарь пользователей, ключом будет телеграмм-ид пользователя, значением - экземпяр класса User
user_dict = {}

# определение класса User
class User:
    def __init__(self, name):
        self.partition = None

# получение пути к вышестоящему каталогу для кнопки Назад
def get_new_partname(partition, separator):
    if partition+'\\'==path2Rootdir:
        return path2Rootdir
    pathlist = partition.split(separator)
    pathlist.pop()
    new_partition = separator.join(pathlist)
    return new_partition

# отправка файлов или их содержимого в ответ
def send_resp(chat_id, path2file):
    if os.path.splitext(path2file)[1]=='.txt':
        bot.send_message(chat_id, read_textfile(path2file))       
    elif os.path.splitext(path2file)[1]=='.jpg' or os.path.splitext(path2file)[1]=='.png' or os.path.splitext(path2file)[1]=='.jpeg':
        bot.send_photo(chat_id, open(path2file, 'rb'))
    else:
        bot.send_document(chat_id, open(path2file, 'rb'))

def read_textfile(path2file):
    return open(path2file)

# определить картинку кнопки по типу значения
def set_btn_image(filename):
    if os.path.isdir(filename):
        btn_img = "📁"
    else:
        if os.path.splitext(filename)[1]=='.txt': 
            btn_img = "📃"
        elif os.path.splitext(filename)[1]=='.jpg' or os.path.splitext(filename)[1]=='.png' or os.path.splitext(filename)[1]=='.jpeg':
            btn_img = "🎑"
        elif os.path.splitext(filename)[1]=='.pdf' or os.path.splitext(filename)[1]=='.doc' or os.path.splitext(filename)[1]=='.docx':
            btn_img = "📝"
        elif os.path.splitext(filename)[1]=='.html' or os.path.splitext(filename)[1]=='.htm':
            btn_img = "📋"
        else:
            btn_img = '❓'
    return btn_img

# генераци кнопок для текущего раздела-каталога
def gen_markup(dirname, uplink):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=False)
    markup.row_width = 3
    counter = 0
    for filename in os.listdir(dirname):
        if os.path.splitext(dirname+'\\'+filename)[1]=='.ini':
            continue
        if counter==0:
            markup.add(set_btn_image(dirname+'\\'+filename)+' '+filename)
        else:
            markup.row(set_btn_image(dirname+'\\'+filename)+' '+filename)
        counter = counter+1
    if uplink == 0:
        markup.add("🔙 Назад","🔝 В главное меню")
    return markup

# отправка приветствия
def send_invitation(message, user):
    user.partition = path2Rootdir
    bot.send_message(message.chat.id, 'Выберите нужную категорию! 👇',reply_markup=gen_markup(path2Rootdir,1))

# разбор сообщения пользователя и выбор ответа
def callback_query(message, user):
    path2dir = user.partition
    is_top_menu = 0
    if user.partition!=path2Rootdir:
        path_separator = '\\'
    else:
        path_separator = ''

    if message.text == "🔙 Назад":
        user.partition = get_new_partname(path2dir, path_separator)
    else: 
        path2target = message.text[2:]
        user.partition = path2dir+path_separator+str(path2target)

    if os.path.isdir(user.partition):
        if user.partition+'\\' == path2Rootdir or user.partition == path2Rootdir:
            is_top_menu = 1

        if is_top_menu == 1:
            partlabel = 'Выберите нужную категорию! 👇'
        else:
            partlabel = user.partition.replace(path2Rootdir, '')
            partlabel = "Раздел: "+partlabel.replace('\\', '|')

        bot.send_message(message.chat.id, partlabel, reply_markup=gen_markup(user.partition,is_top_menu))
    else:
        send_resp(message.chat.id, user.partition)
        user.partition = user.partition.replace(path_separator+str(path2target), '')

# обработка стартовой команды
@bot.message_handler(commands=['start', 'help'])
def send_hellow(message):
    hellow_text = """Привет✋ Я бот-справочник 📕 
👉 Для вызова меню - отправьте мне ЛЮБОЕ текстовое сообщение.
👉 Для навигации по меню - используйте клавиатуру. 
❗ Файлы я обрабатывать пока не умею! Поэтому, если отправите мне фото или файл - я его проигнорирую!"""
    bot.send_message(message.chat.id, hellow_text)

# обработка событий-хэндлеров
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    chat_id = message.chat.id
    try:
        user = user_dict[chat_id]
    except Exception:
        user = User(chat_id)
        user_dict[chat_id] = user    
    if user.partition == None or message.text == "🔝 В главное меню":
        send_invitation(message, user)
    else:
        try:
            callback_query(message, user)
        except Exception:
            send_invitation(message, user)


# Enable saving next step handlers to file "./.handlers-saves/step.save".
# Delay=2 means that after any change in next step handlers (e.g. calling register_next_step_handler())
# saving will hapen after delay 2 seconds.
bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

while True:
    try:
      bot.polling(none_stop=True)

    except Exception:
         #logger.error(e)  # или просто print(e) если у вас логгера нет,
         # или import traceback; traceback.print_exc() для печати полной инфы
         time.sleep(5)