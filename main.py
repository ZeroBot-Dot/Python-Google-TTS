import requests
import os
import multiprocessing
import time
import random
import configparser
import base64
import json

configF = configparser.ConfigParser()
configF.read("config.ini")
nameBook = str(configF['book']['nameBook'])
f = open(nameBook)
text = f.read()
f.close()
data = (
        '{"input":{"text":"' + text + '"},"voice":{"languageCode":"ru-RU","name":"ru-RU-Wavenet-D"},"audioConfig":{"audioEncoding":"LINEAR16","pitch":0,"speakingRate":0.8}}').encode(
    'utf-8')
try:
    f = open(str(configF['book']['glossary']))
    config = f.read()
    f.close()
except:
    print('Отсутствует словарь!')
    config = ''

config = config.replace('"', '')
config = config.split('=')
zabiv = 1
text = text.replace('"', ";").replace('.', " .")
print("начинается замена")
while zabiv + 1 < len(config):
    text = text.replace(str(config[zabiv].split('\n')[1]), str(config[zabiv + 1].split('\n')[0]))
    zabiv = zabiv + 1
print("заменено успешно")
text = text.split('\n')
i = 0

i = i + 1
text2 = text[i]


def compil(i, textjs):
    global configF
    direct = str(configF['book']['directory'])
    filename = str(configF['book']['filename'])
    audio_content = textjs
    try:
        f = open(direct + '/' + filename + str(i) + '.mp3', 'wb')
    except:
        os.mkdir(direct)
        f = open(direct + '/' + filename + str(i) + '.mp3', 'wb')

    f.write(base64.b64decode(audio_content))
    f.close()


def razbivN(text):
    i = 0
    ii = 0
    ioi = [0]
    text2 = ''
    while (len(text) - 1) > i:
        try:
            text2 = ''
            while len(text2 + '\n' + str(text[i + 1])) < 4999:
                i = i + 1
                if text2 != str(text[i]):
                    text2 = text2 + '\n' + str(text[i])
            ioi.append(i)
        except:
            i = i

        ii += 1
    return (ii, ioi)


def razbiv(lii, text):
    i = lii
    text2 = ''
    try:
        while len(text2 + '\n' + str(text[i + 1])) < 4999:
            i = i + 1
            if text2 != str(text[i]):
                text2 = text2 + '\n' + str(text[i])
    except:
        print('усе')
    return (text2)


def sendText(text2, data, i):
    global configF
    token = str(configF['book']['token'])
    speed = str(configF['book']['speed'])
    headers = {
        'authority': 'cxl-services.appspot.com',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="92"',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0',
        'content-type': 'text/plain;charset=UTF-8',
        'accept': '*/*',
        'origin': 'https://www.gstatic.com',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.gstatic.com/',
        'accept-language': 'ru-RU,ru;q=0.9',
    }
    params = (
        ('url', 'https://texttospeech.googleapis.com/v1beta1/text:synthesize'),
        ('token', token),
    )
    error = 1
    while error != 0:
        data = ('{"input":{"text":"' + str(text2) + '"},"voice":{"languageCode":"ru-RU","name":"' + str(
            configF['book']['name']) + '"},"audioConfig":{"audioEncoding":"' + str(
            configF['book']['audioEncoding']) + '","pitch":0,"speakingRate":' + speed + '}}').encode('utf-8')
        response = requests.post('http://cxl-services.appspot.com/proxy', headers=headers, params=params, data=data)
        response = response.text.encode().decode()
        error = 0
        if response != '' and response != ' Service Unavailable' and response != 'Service Unavailable' and response != 'Unauthorized':
            response = json.loads(response)["audioContent"]
            error = 0
        else:
            print('Произошло что то не то. Скорее всего у вас устарел токен.')
            print(response)
            time.sleep(60)
            error += 1
        if len(response) < 200:
            print(response)
            print(len(str(text2)))
            error += 1
        else:
            print('успешно ' + str(i))
            compil(i, response)
            return (i, text2)


def osnov(text, trii, lli):
    text2 = razbiv(lli[trii], text)
    sendTex = sendText(text2, data, trii)
    i = sendTex[0]
    text2 = sendTex[1]
    return (i)


ii = razbivN(text)
lli = ii[1]
ii = int(ii[0])
trii = int(configF['book']['start'])
boolThreads = int(configF['book']['threads'])
if boolThreads > int(multiprocessing.cpu_count()):
    boolThreads = int(multiprocessing.cpu_count())
    print('вы выставили слишком большое кол-во потоков, ваш пк не поддерживает столько.')
while trii < ii:
    if len(multiprocessing.active_children()) < boolThreads:
        print(str(trii) + '(' + str((trii * 100) // ii) + '%)')
        my_thread = multiprocessing.Process(target=osnov, args=(text, trii, lli,))
        my_thread.start()
        trii += 1
        time.sleep(1)
