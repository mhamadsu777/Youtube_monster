import telebot
import pytube
import os
import requests
from info import token,sudo_channel,sudo_username

bot = telebot.TeleBot("1604318595:AAHj1rkg60SW_cbsA8t7TwDyYPxas2stAso")
video = None


def create_keyboard(yt):
    buttons = []
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    i = 0
    for stream in yt.streams.filter(progressive='True'):
        typ = str(stream).split(' ')[2].split('=')[1][1:-1]
        quality = str(stream).split(' ')[3].split('=')[1][1:-1]

        text_but = 'تحميل'
        buttons.append(telebot.types.InlineKeyboardButton(text=text_but, callback_data=str(i)))
        i += 1
    keyboard.add(*buttons)
    return keyboard

url = f"https://api.telegram.org/bot{token}/getChat?chat_id=@{sudo_channel}"
response = requests.get(url).json()
GetName = response['result']['title']

@bot.message_handler(commands=['start'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "اهلا بك عزيزي في بوت تحميل من يوتيوب \n عن طريق رابط الفيديو \n يمكنك استخدام @vid للبحث \n معرف المطوري : @{} ".format(sudo_username))


@bot.message_handler(commands=['source'])
def get_text_messages(message):
    bot.send_message(message.from_user.id, "[{}](t.me/{})".format(GetName,sudo_channel), parse_mode="markdown")



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    yt = None
    try:
        yt = pytube.YouTube(message.text)
    except pytube.exceptions.RegexMatchError:
        bot.send_message(message.from_user.id, "لا استطيع تحميل هذا الملف. تحقق من رابط")
    if yt is not None:
        keyboard = create_keyboard(yt)
        global video
        video = yt
        bot.send_message(message.from_user.id, 'اختر تنسيقًا للتنزيل', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda x: True)
def callback_handler(callback_query):
    global video
    bot.send_message(callback_query.from_user.id, "جاري التحميل .....")
    video = open(video.streams.filter(progressive='True')[int(callback_query.data)].download(
                 filename='@{}'.format(sudo_channel)), 'rb')
    bot.send_audio(callback_query.from_user.id, video)
    video.close()
    os.remove('@{}'.format(sudo_channel))


bot.polling()