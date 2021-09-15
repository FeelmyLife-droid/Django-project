import json
from datetime import datetime, timedelta

import telebot
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt

API_TOKEN = ''
bot = telebot.TeleBot(token=API_TOKEN)



@csrf_exempt
def example(request):
    d = datetime.now() + timedelta(hours=3)
    date = d.strftime("%d.%m.%Y %H:%M")

    if request.method == 'POST':
        print(request.POST)
        response = request.POST
        sms = json.loads(response['result'])
        message = f'Дата: {date}\nКому: {my_firm.get(sms.get("caller_did"))}\nОт: {sms.get("caller_id")}\nТекст: {sms.get("text")}\n'
        bot.send_message(chat_id=, text=message)
        bot.send_message(chat_id=, text=sms)
        return HttpResponse(request)

    elif request.method == 'GET':
        print(date)
        print(request.GET['zd_echo'])
        return HttpResponse(request.GET['zd_echo'])
