from encodings.base64_codec import base64_encode
import json

import telebot
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

API_TOKEN = '1201963552:AAHsOn56nBBxrG7ybH7ud7ieK8dnaRIs2_E'
bot = telebot.TeleBot(token=API_TOKEN)


@csrf_exempt
# @require_POST
def example(request):
    # try:
    # response = request.POST
    # sms = json.loads(response['result'])
    # message = f'КОМУ:{sms.get("caller_did")}\nОТ:{sms.get("caller_id")}\nТЕКСТ:{sms.get("text")}\n'
    # bot.send_message(chat_id=589574396, text=message)
    return HttpResponse(request)
    # except:
    #     return HttpResponse(request)
