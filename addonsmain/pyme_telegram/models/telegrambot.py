# -*- coding: utf-8 -*-

import time
import requests


def telegram_bot_sendtext(bot_message):
    
    bot_token = '1730507116:AAEbitOTTnIefEnJE43EB5B5bUuEHxEYzEk'
    bot_chatID = '1060565088'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


my_message="Hola PEPE"
telegram_bot_sendtext(my_message)


