import json
from datetime import datetime, timedelta

import telebot
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

API_TOKEN = '1201963552:AAHsOn56nBBxrG7ybH7ud7ieK8dnaRIs2_E'
bot = telebot.TeleBot(token=API_TOKEN)
my_firm = {
    '79675559239': 'KPT',
    '79675556381': 'raketa',
    '79675551853': 'ECOPORODYKT',
    '79675559213': 'POBEDA',
    '79675559267': 'SY',
    '79581110941': 'TLK',
    '79675557624': 'AVTOPILOT',
    '79675559382': 'VOSTOK',
    '79581119261': 'INKOM',
    '79699996782': 'VOZKOM',
    '79675559363': 'SPK21',
    '79581110452': 'ZERNOMUKA',
    '79699996752': 'Delavto',
    '79675559317': 'OPT',
    '79675558375': 'ALTRAK',
    '79675559716': 'PARSER',
    '79675553216': 'AVTOPILOT',
    '79675559671': '79675559671',
    '79675559634': '79675559634',
    '79675559662': '79675559662'
}


@csrf_exempt
def example(request):
    d = datetime.now() + timedelta(hours=3)
    date = d.strftime("%d.%m.%Y %H:%M")

    if request.method == 'POST':
        print(request.POST)
        response = request.POST
        sms = json.loads(response['result'])
        message = f'Дата: {date}\nКому: {my_firm.get(sms.get("caller_did"))}\nОт: {sms.get("caller_id")}\nТекст: {sms.get("text")}\n'
        bot.send_message(chat_id=981649320, text=message)
        bot.send_message(chat_id=589574396, text=sms)
        return HttpResponse(request)

    elif request.method == 'GET':
        print(date)
        print(request.GET['zd_echo'])
        return HttpResponse(request.GET['zd_echo'])
