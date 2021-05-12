import os
import sys
import json
import youtube_dl
import telepotpro
from info import token,sudo_channel,sudo_username
from random import randint
from multiprocessing import Process
from youtubesearchpython import SearchVideos

bot = telepotpro.Bot("1604318595:AAHj1rkg60SW_cbsA8t7TwDyYPxas2stAso")
def create_keyboard(yt):
    buttons = []
    keyboard = telepotpro.types.InlineKeyboardMarkup(row_width=1)
    i = 0
    for stream in yt.streams.filter(progressive='True'):
        typ = str(stream).split(' ')[2].split('=')[1][1:-1]
        quality = str(stream).split(' ')[3].split('=')[1][1:-1]

        text_but = 'تحميل'
        buttons.append(telepotpro.types.InlineKeyboardButton(text=text_but, callback_data=str(i)))
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
def startMsg(chat_id, first_name):
	bot.sendMessage(chat_id, '*ميزة اليوتيوب تعمل بشكل جيد*', parse_mode= 'Markdown')

def errorMsg(chat_id, error_type):
	if error_type == 'too_long':
		bot.sendMessage(chat_id, 'يرجى اختيار الفنان واسم الاغنية بشكل جيد ', parse_mode= 'Markdown')

def downloadMusic(file_name, link):
	ydl_opts = {
		'outtmpl': './'+file_name,
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '256',
		}],
		'prefer_ffmpeg': True
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		info_dict = ydl.extract_info(link, download=True)

def validMusicInput(userInput, chat_id, chat_type):
		#Search music on youtube
		search = SearchVideos(userInput[6:], offset = 1, mode = "json", max_results = 1)
		resultados = json.loads(search.result())
		
		#Get video duration
		duration = resultados['search_result'][0]['duration'].split(':')
		splitCount = len(duration)

		if int(duration[0]) < 30 and splitCount < 3:
			title = resultados['search_result'][0]['title']
			link = resultados['search_result'][0]['link']
			file_name = title +' - '+str(randint(0,999999))+'.mp3'

			bot.sendMessage(chat_id,'🎵 '+title+'\n'+'🔗 '+link)
			DownloadingMsg = bot.sendMessage(chat_id,'*جار التحميل (قد يستغرق بعض الوقت يرجى الانتظار)*', parse_mode= 'Markdown')

			#Download the music
			downloadMusic(file_name, link)

			bot.sendAudio(chat_id,audio=open(file_name,'rb'))
			bot.deleteMessage((chat_id, DownloadingMsg['message_id']))
			bot.sendMessage(chat_id, '*تم التنزيل بنجاح*', parse_mode= 'Markdown')
			print ("نجح")
			os.remove(file_name)

		else:
			errorMsg(chat_id, 'too_long')

		pass

def recebendoMsg(msg):
	userInput = msg['text']
	chat_id = msg['chat']['id']
	first_name = msg['from']['first_name']
	chat_type = msg['chat']['type']

	if chat_type == 'group':
		if '@TLMusicDownloader_bot' in userInput:
			userInput = userInput.replace('@TLMusicDownloader_bot', '')

	elif userInput.startswith('بحث') and userInput[6:]!='':
		if 'open.spotify.com' in userInput[6:]:
			errorMsg(chat_id, 'spotify_command')

		else:
			#Process the music
			validMusicInput(userInput, chat_id, chat_type)

	else:
		#Invalid command
		errorMsg(chat_id, 'invalid_command')

	pass

def main(msg):
	main_process = Process(target=recebendoMsg, args=(msg,))
	main_process.start()

bot.message_loop(main, run_forever=True)
