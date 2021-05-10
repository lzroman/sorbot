#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
from sorbot_core import sorbot_core
from vk_api.longpoll import VkChatEventType
from vk_api.bot_longpoll import VkBotEventType
import time, random
from threading import Thread
import datetime
import json
import requests
#from pydub import AudioSegment
import numpy as np
import math
from PIL import Image
import json
from pathlib import Path
from gtts import gTTS

#import discord



class sorbot:
    def __init__(self, token, bot_id, botname, admin_ids):
        if 'utoken' in conf.keys():
            self.core = sorbot_core(conf['token'], conf['utoken'])
        else:
            self.core = sorbot_core(conf['token'])
        print(self.core.vk_session.method('messages.getConversations',{'count' : 10}))
        self.bot_id = conf['bot_id']
        self.admin_ids = conf['admin_ids']
        self.botname = conf['botname'].lower()
        self.plugins = []
        self.plugins_run = []
        self.actions = []
        self.threads = []
        self.admin_list = []
        self.chats_conf = []
        self.chats = {}#{'plugins': [], 'plugins_run': [], 'actions': [], 'threads': []}
        #self.get_admins()
        '''with open('chat_conf.json', 'r') as f:
            chat_file = json.load(f)
            self.chats_conf = chat_file.copy()'''
        self.gparms = {'bot_id': self.bot_id, 'botname': self.botname, 'chat_admins': self.admin_list, 'achievements': {}, 'achievements_original': {}, 'ach_len': 0, 'stats_original': {}, 'stats': {}, 'help': [], 'help_t': '', 'plugins': {}}
        self.gparms['is_ach_on_user'] = self.is_ach_on_user
        self.gparms['achieve'] = self.achieve
        self.gparms['is_stat_on_user'] = self.is_stat_on_user
        self.saving_ach_thread = Thread(target=self.saving_ach)
        self.saving_ach_thread.start()
        self.achieve_thread_onject = Thread()
    
    def plugins_add(self, plugin):
        self.plugins.append(plugin)
    
    def start(self):
        self.watcher = Thread(target=self.start_internal)
        self.watcher.start()
        while True:
            inp = input()
            if inp == 's':
                with open('achievements.json', 'w') as outfile:
                    json.dump(self.gparms['achievements'], outfile)
                with open('stats.json', 'w') as outfile:
                    json.dump(self.gparms['stats'], outfile)
                with open('plugins.json', 'w') as outfile:
                    json.dump(self.gparms['plugins'], outfile)
                break
            if inp == 'f':
                upload = self.core.upload.photo_messages('bye.jpg')[0]
                self.core.vk.messages.send(message='Прощайте.', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))


    def saving_ach(self):
        time.sleep(600)
        while True:
            with open('achievements.json', 'w') as outfile:
                json.dump(self.gparms['achievements'], outfile)
            with open('stats.json', 'w') as outfile:
                json.dump(self.gparms['stats'], outfile)
            with open('plugins.json', 'w') as outfile:
                json.dump(self.gparms['plugins'], outfile)
            time.sleep(600)

    def start_internal(self):
        for plugin in self.plugins:
            self.plugins_run.append(plugin(self.core, self.gparms))
        for plugin in self.plugins_run:
            newach = plugin.achievements()
            for ach in newach:
                self.gparms['achievements_original'][ach] = newach[ach].copy()
            newstat = plugin.stats()
            for stat in newstat:
                self.gparms['stats_original'][stat] = newstat[stat].copy()
            newhelp = plugin.help()
            for helpp in newhelp:
                self.gparms['help'].append(helpp)
            for action in plugin.actions():
                self.actions.append(action)
        for helpp in self.gparms['help']:
            self.gparms['help_t'] += '\n- ' + helpp

        with open('achievements.json', 'r') as f:
            ach_file = json.load(f)
            self.gparms['achievements'] = ach_file.copy()

        with open('stats.json', 'r') as f:
            stats_file = json.load(f)
            self.gparms['stats'] = stats_file.copy()
        with open('plugins.json', 'r') as f:
            plugins_file = json.load(f)
            self.gparms['plugins'] = plugins_file.copy()
        print(self.gparms['plugins'])
        #print(self.gparms['achievements'])
        #print(self.gparms['stats'])

        self.gparms['ach_len'] = len(self.gparms['achievements_original'])
        while True:
            events = self.core.getevents()
            for event in events:
                if event.from_chat:
                    if event.chat_id not in self.chats.keys():
                        self.chats[event.chat_id] = self.newchat(event.chat_id).copy()
                    for action in self.chats[event.chat_id]['actions']:
                        self.chats[event.chat_id]['threads'].append(Thread(target=self.execute_action,args=(action,event)))
                        self.chats[event.chat_id]['threads'][-1].start()
            for chat in self.chats.keys():
                for thread in self.chats[chat]['threads']:
                    if not thread.is_alive():
                        self.chats[chat]['threads'].remove(thread)
            events.clear()

    def newchat(self, chat_id):
        chatobj = {'plugins_run': [], 'actions': [], 'threads': []}
        for plugin in self.plugins:
            chatobj['plugins_run'].append(plugin(self.core, self.gparms))
        for plugin in chatobj['plugins_run']:
            for action in plugin.actions():
                chatobj['actions'].append(action)
        return chatobj

    def achieve(self, ach, user):
        self.achieve_thread_onject = Thread(target=self.achieve_thread,args=(ach,str(user)))
        self.achieve_thread_onject.start()

    def achieve_thread(self, ach, user):
        if not self.gparms['achievements'][user][ach]['state']:
            self.gparms['achievements'][user][ach]['state'] = True
            #if 'img' in self.gparms['achievements_original'][ach]:
                #upload = self.core.upload.photo_messages(self.gparms['achievements_original'][ach]['img'])[0]
                #time.sleep(5)
                #self.core.vk.messages.send(message='@id' + str(user) + '(' + self.core.vk_session.method('users.get',{'user_id' : user})[0]['first_name'] + '), вы получили новое достижение - "' + self.gparms['achievements_original'][ach]['text'] + '"!\n' + self.gparms['achievements_original'][ach]['desc'],chat_id=event.chat_id, random_id=vk_api.utils.get_random_id(),attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
            #else:
                #self.core.send_message('@id' + str(user) + '(' + self.core.vk_session.method('users.get',{'user_id' : user})[0]['first_name'] + '), вы получили новое достижение - "' + self.gparms['achievements_original'][ach]['text'] + '"!\n' + self.gparms['achievements_original'][ach]['desc'],chat_id=event.chat_id)

    def is_stat_on_user(self, stat, user):
        uname = str(user)
        if uname in self.gparms['stats'].keys():
            if stat not in self.gparms['stats'][uname].keys():
                self.gparms['stats'][uname][stat] = self.gparms['stats_original'][stat]['params'].copy()
        else:
            self.gparms['stats'][uname] = {}
            self.gparms['stats'][uname][stat] = self.gparms['stats_original'][stat]['params'].copy()


    def is_ach_on_user(self, ach, user):
        uname = str(user)
        if uname in self.gparms['achievements'].keys():
            if ach not in self.gparms['achievements'][uname].keys():
                self.gparms['achievements'][uname][ach] = self.gparms['achievements_original'][ach]['params'].copy()
        else:
            self.gparms['achievements'][uname] = {}
            self.gparms['achievements'][uname][ach] = self.gparms['achievements_original'][ach]['params'].copy()

    def execute_action(self, action, event):
        try:
            action(event)
        except Exception as e:
            #self.error_log(e)
            print(e, flush=True)
    
    def error_log(self, text):
        for admin in self.admin_ids:
            self.core.send_message('Братан, мне чот фигова:\n' + str(text),user_id = admin)





#plugin template
class template:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms

    def achievements(self):
        return {'ach':{'text':'','img':'','desc':'','params':{'state':False}}}

    def actions(self):
        return [self.action]
    
    def action(self, event):
        pass

    def stats(self):
        return {'stat':{'text':'','params':{'value':0}}}

    def help(self):
        return []








class huy:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.starttime = datetime.datetime(2020,5,5)
        self.is_running = False
        self.timeout = 2
        self.bigtimeout = 10
        self.glas_y = 'еёюяй'
        self.glas = 'аиоуыэ'
        self.sogl_zv = 'сзж'
        self.sogl = 'бвгдзклмнпрстфхжцшщчй'

    def achievements(self):
        #return {'first_huy':{'text':'ХуйНя!','desc':'Первая игра в карательную рулетку','params':{'state':False,'count':0}}}
        return {}

    def actions(self):
        return [self.action]
    
    def action(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if len(event.message.text):
                if event.from_chat:
                    if event.message.from_id != 379124050:
                        ctime = datetime.datetime.now()
                        if self.is_running and ((ctime - self.starttime).total_seconds() < self.timeout * 60):
                            if event.message.text.lower() == "карбот стопхуй" or event.message.text.lower() == "карбот стопчлен":
                                self.is_running = False
                                self.core.send_message('Хорошо, больше никаких хуёв.',chat_id=event.chat_id,forward_messages=None)
                            else:
                                text = self.makehui(event.message.text)
                                if text:
                                    self.core.send_message(text,chat_id=event.chat_id,forward_messages=None)
                        elif event.message.text.lower() == "карбот хуй" or event.message.text.lower() == "карбот член":
                            if event.message.reply_message:
                                text = self.parsereply(event.message.reply_message)
                                if text:
                                    self.core.send_message(text,chat_id=event.chat_id,forward_messages=None)
                            elif len(event.message.fwd_messages):
                                text = self.parsefwd(event.message.fwd_messages)
                                if text:
                                    self.core.send_message(text,chat_id=event.chat_id,forward_messages=None)
                            else:
                                if (ctime - self.starttime).total_seconds() < self.bigtimeout * 60:
                                    self.core.send_message('Слишком рано, упырьте мел.',chat_id=event.chat_id,forward_messages=None)
                                else:
                                    self.core.send_message('Понеслась.',chat_id=event.chat_id,forward_messages=None)
                                    self.starttime = datetime.datetime.now()
                                    self.is_running = True


    def parsereply(self, obj):
        return self.parse_in(obj)

    def parsefwd(self, obj):
        ans = ''
        if len(obj):
            for subobj in obj:
                ans += self.parse_in(subobj) + '\n'
        return ans

    def parse_in(self, obj):
        ans = ''
        if 'reply_message' in obj.keys():
            ans += self.parse_in(obj['reply_message']) + '\n'
        if 'fwd_messages' in obj.keys():
            for subobj in obj['fwd_messages']:
                ans += self.parse_in(subobj) + '\n'
        if 'text' in obj.keys():
            if len(obj['text']) > 0:
                ans += self.makehui(obj['text']) + '\n'
        return ans

    def makehui(self, msg):
        if len(msg):
            text = ''
            words = msg.lower().split()
            for word in words:
                text += self.makehuy(word) + ' '
            return text

    def makehuy(self, word):
        text = ''
        if word[0] in self.glas_y:
            text = 'ху' + word
        # elif word[0] in self.sogl_zv:
        #     text = 'хуе' + word
        else:
            gas = self.is_glas_and_sogl(word)
            if gas:
                if word[gas] in self.glas_y:
                    text = 'ху' + word[gas:]
                else:
                    text = 'ху' + self.yeti(word[gas-1]) + word[gas:]
            else:
                say = self.is_sogl_and_y(word)
                if say:

                    text = 'ху' + word[say:]
                else:
                    sagas = self.is_sogl_and_glas_and_sogl(word)
                    if sagas:
                        if word[sagas] in self.glas_y:
                            text = 'ху' + word[sagas:]
                        else:
                            text = 'ху' + self.yeti(word[sagas-1]) + word[sagas:]
                    elif self.is_all_sogl(word):
                        text = 'ху'+ word
                    elif self.is_all_glas(word):
                        text = 'хуе'+ self.yeti(word[0]) + word[1:]

        if not len(text):
            text = word
        return text
        

    def is_glas_and_sogl(self, word):
        wordlen = len(word)
        i = 0
        while i < wordlen and word[i] in self.glas:
            i += 1
        if not i or i == wordlen:
            return False
        if word[i] in self.sogl or word[i] in self.glas_y:
            return i
        return 0
        
    def yeti(self, glas):
        if glas == 'а':
            return 'я'
        if glas == 'и' or glas == 'ы':
            return 'и'
        if glas == 'о':
            return 'ё'
        if glas == 'у':
            return 'ю'
        if glas == 'э':
            return 'е'

    def is_sogl_and_y(self, word):
        wordlen = len(word)
        i = 0
        while i < wordlen and word[i] in self.sogl:
            i += 1
        if not i or i == wordlen :
            return 0
        if word[i] in self.glas_y:
            return i
        return 0

    def is_sogl_and_glas_and_sogl(self, word):
        wordlen = len(word)
        i = 0
        while i < wordlen and word[i] in self.sogl:
            i += 1
        while i < wordlen and word[i] in self.glas:
            i += 1
        if not i or i == wordlen :
            return 0
        if word[i] in self.sogl or word[i] in self.glas_y:
            return i
        return 0

    def is_all_glas(self, word):
        is_all = True
        for b in word:
            if b not in self.glas:
                is_all = False
                break
        return is_all

    def is_all_sogl(self, word):
        is_all = True
        for b in word:
            if b not in self.sogl and b not in self.glas_y:
                is_all = False
                break
        return is_all


    def stats(self):
        return {}

    def help(self):
        return [' По командам "карбот хуй" и "карбот член" хуефицирует прикреплённое сообщение или, если прикрепа нет, начнёт массовую хуификацию сообщений']






class daily_pidor:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.pidor = 0
        self.itime = datetime.datetime.now()
        if 'pidor' not in self.gparms['plugins']:
            self.gparms['plugins']['pidor'] = {}
        else:
            newd = {}
            for key in self.gparms['plugins']['pidor'].keys():
                newd[int(key)] = self.gparms['plugins']['pidor'][key]
            self.gparms['plugins']['pidor'] = newd
        #self.init(silent=True)
        self.words = [
            [
            'Сказал',
            'Подметил',
            'Кукарекнул',
            'Вякнул',
            'Спизданул, не подумавши,',
            'Пукнул',
            'Высрал',
            'Пиздобрякнул',
            'Выебнулся',
            'Промямлил',
            'Хуйнул',
            'Жидко пёрнул'
            ],
            [
            'пидор',
            'пидорас',
            'хуесос',
            'спермоглот',
            'хуепутало',
            'ебанат',
            'членосос',
            'заднеприводный',
            'очкоприёмник',
            'жополаз',
            'властелин коричневой бездны',
            'dungeon master',
            'гомосексуалист',
            'Чарли из шоколадной фабики',
            'Boss of this gym'
            ]
        ]

    def achievements(self):
        return {}

    def actions(self):
        return [self.action, self.whois]

    def stats(self):
        return {}

    def help(self):
        return ['Каждый день избирается пидор дня, на которого бот должным образом реагирует. Включить функцию - "карбот пидор включи", выключить - очевидно. Узнать героя - "карбот пидор" или "карбот герой". Сменить сиюмоментно - "карбот сменщик" или "карбот сменщик @пользователь", сменять могут только администраторы беседы.']
    
    def init(self, chat_id, silent=False):
        print('init daily_pidor')
        ulist =  self.core.vk_session.method('messages.getConversationMembers',{'peer_id' : 2000000000 + chat_id, 'fields': 'users'})['profiles']
        pidor = random.choice(ulist)['id']
        self.gparms['plugins']['pidor'][chat_id] = {}
        self.gparms['plugins']['pidor'][chat_id]['id'] = pidor
        self.gparms['plugins']['pidor'][chat_id]['name'] = self.core.vk_session.method('users.get',{'user_id' : pidor})[0]['first_name']
        self.gparms['plugins']['pidor'][chat_id]['time'] = datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(minutes=31))
        print('pidor is ', self.gparms['plugins']['pidor'][chat_id]['name'], ' ', str(pidor))
        if not silent:
            self.core.send_message('@id' + str(pidor) + '(' + self.gparms['plugins']['pidor'][chat_id]['name'] + '), теперь вы - пидор дня. Наслаждайтесь вашим статусом!',chat_id=chat_id)
        print('done')

    def action(self, event):
        time = datetime.datetime.now()
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id in self.gparms['plugins']['pidor']:
                    ctime = datetime.datetime.now()
                    if event.message.from_id == self.gparms['plugins']['pidor'][event.chat_id]['id']:
                        if (ctime - datetime.datetime.fromtimestamp(self.gparms['plugins']['pidor'][event.chat_id]['time'])).total_seconds() > 30 * 60:
                            self.gparms['plugins']['pidor'][event.chat_id]['time'] = datetime.datetime.timestamp(datetime.datetime.now())
                            self.core.send_message(random.choice(self.words[0]) + ' ' + random.choice(self.words[1]) + ' @id' + str(self.gparms['plugins']['pidor'][event.chat_id]['id']) + '(' + self.gparms['plugins']['pidor'][event.chat_id]['name'] + ').',chat_id=event.chat_id,forward_messages=None)
                    if datetime.datetime.fromtimestamp(self.gparms['plugins']['pidor'][event.chat_id]['time']).day != ctime.day:
                        if ctime.hour > 19:
                            self.init(event.chat_id)
                    
                    words = event.message.text.lower().split()
                    if words[0] == 'карбот' and words[1] == 'пидор' and words[2] == 'выключи':
                        self.core.send_message('Функция Пидор дня отключена.',chat_id=event.chat_id,forward_messages=None)
                else:
                    words = event.message.text.lower().split()
                    if words[0] == 'карбот' and words[1] == 'пидор' and words[2] == 'включи':
                        self.core.send_message('Функция Пидор дня включена.',chat_id=event.chat_id,forward_messages=None)
                        self.init(event.chat_id)


    def whois(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id in self.gparms['plugins']['pidor'].keys():
                    if event.message.text.lower() == 'карбот пидор' or event.message.text.lower() == 'карбот герой':
                        self.gparms['plugins']['pidor'][event.chat_id]['name'] = self.core.vk_session.method('users.get',{'user_id' : self.gparms['plugins']['pidor'][event.chat_id]['id']})[0]['first_name']
                        self.core.send_message('Сегодняшний пидор - @id' + str(self.gparms['plugins']['pidor'][event.chat_id]['id']) + '(' + self.gparms['plugins']['pidor'][event.chat_id]['name'] + ').',chat_id=event.chat_id,forward_messages=None)
                    #if event.message.from_id in self.gparms['chat_admins']:
                    words = event.message.text.lower().split()
                    if words[0] == 'карбот' and words[1] == 'сменщик':
                        admin_list = []
                        ans = self.core.vk_session.method('messages.getConversationMembers',{'peer_id' : event.chat_id + 2000000000})
                        for user in ans['items']:
                            if 'is_admin' in user:
                                if user['is_admin']:
                                    admin_list.append(user['member_id'])
                        if event.message.from_id in admin_list:
                            if len(words) == 2:
                                self.init(event.chat_id)
                            elif words[2] == 'тихо':
                                self.init(event.chat_id, silent=True)
                            else:
                                print(words)
                                if words[2][0] == '[':
                                    npos = words[2].find('|')
                                    print(npos)
                                    if npos != -1:
                                        try:
                                            ans = self.core.vk_session.method('utils.resolveScreenName', {'screen_name' : words[2][1:npos]})
                                        except Exception as e:
                                            print(''.join(['fail: ', e]))
                                        print(ans)
                                        if len(ans):
                                            if ans['type'] == 'user':
                                                uid = self.core.vk_session.method('users.get',{'user_id' : [int(words[2][3:npos])]})[0]['id']
                                                print(uid)
                                                if words[-1] == 'тихо':
                                                    self.forceinit(event.chat_id, uid, silent=True)
                                                else:
                                                    self.forceinit(event.chat_id, uid)



    def forceinit(self, chat_id, uid, silent=False):
        ulist =  self.core.vk_session.method('messages.getConversationMembers',{'peer_id' : 2000000000 + chat_id, 'fields': 'users'})['profiles']
        uids = [user['id'] for user in ulist]
        if uid in uids:
            self.itime = datetime.datetime.now()
            self.gparms['plugins']['pidor'][chat_id]['time'] = datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(minutes=31))
            self.gparms['plugins']['pidor'][chat_id]['id'] = uid
            self.gparms['plugins']['pidor'][chat_id]['name'] = self.core.vk_session.method('users.get',{'user_id' : self.gparms['plugins']['pidor'][chat_id]['id']})[0]['first_name']
            print('pidor is ', self.gparms['plugins']['pidor'][chat_id]['name'], ' ', str(self.pidor))
            if not silent:
                self.core.send_message('@id' + str(self.gparms['plugins']['pidor'][chat_id]['name']) + '(' + self.gparms['plugins']['pidor'][chat_id]['name'] + '), теперь вы - пидор дня. Наслаждайтесь вашим статусом!',chat_id=chat_id)
                







class showhelp:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms

    def achievements(self):
        return {}

    def actions(self):
        return [self.action]
    
    def action(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.message.text.lower() == 'карбот помощь' or event.message.text.lower() == 'карбот help' or event.message.text.lower() == 'карбот':
                    print(event.obj.keys())
                    print(event.message.keys())
                    print(event.message.conversation_message_id)
                    self.core.send_message('Доступные функции бота:\n' + self.gparms['help_t'],chat_id=event.chat_id,forward_messages=None)

    def stats(self):
        return {}

    def help(self):
        return ['Команды "карбот", "карбот help" и "карбот помощь" покажут эту справку']


class voicetomusic:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.attachments = []
        self.busy = False

    def achievements(self):
        return {}

    def actions(self):
        return [self.action]

    def help(self):
        return ['Команда "карбот музыка" и прикреплённое сообщение с голосовым сообщением длительностью более 3 секунд вернёт его как аудиозапись']
    
    def action(self, event):
        if self.core.uacc:
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    if event.message.text.lower() == 'карбот музыка':
                        if not self.busy:
                            self.busy = True
                            #print(event.message.conversation_message_id)
                            # answer = self.core.vk_session.method('messages.getById',{'message_ids' : event.message.conversation_message_id})
                            # print(answer)
                            self.fwd(event.raw['object']['message'])
                            if self.attachments:
                                attach_text = ','.join(self.attachments)
                                self.core.vk.messages.send(message='Наслаждайтесь!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment=attach_text)
                            self.attachments.clear()
                            self.busy = False
                        else:
                            self.core.send_message('Я обрабатываю другие аудиозаписи, попробуйте позже.' ,chat_id=event.chat_id,forward_messages=None)
        

    
    def fwd(self, obj):
        if len(self.attachments) < 10:
            #if 'conversation_message_id' in obj.keys():
            #    self.fwd(self.core.vk_session.method('messages.getByConversationMessageId',{'peer_id' : obj['peer_id'], 'conversation_message_ids': obj['conversation_message_id']})['items'][0])
            if 'reply_message' in obj.keys():
                self.fwd(obj['reply_message'])
            if 'fwd_messages' in obj.keys():
                for subobj in obj['fwd_messages']:
                    self.fwd(subobj)
            for attachment in obj['attachments']:
                if attachment['type'] == 'audio_message':
                    if attachment['audio_message']['duration'] > 3:
                        self.attachments.append(self.work(attachment['audio_message']))

    def work(self, link):
        r = requests.get(link['link_mp3'])
        with open('audio.mp3', 'wb') as output_file:
            output_file.write(r.content)
        title = "title"
        if len(link['transcript']):
            if len(link['transcript']) > 200:
                title = link['transcript'][:200]
            else:
                title = link['transcript']
        user = self.core.vk_session.method('users.get',{'user_id' : link['owner_id']})[0]
        upload = self.core.uupload.audio('audio.mp3', user['first_name'] + ' ' + user['last_name'], title)
        #self.core.vk.messages.send(message='Наслаждайтесь!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='audio' + str(upload['owner_id']) + '_' + str(upload['id']))
        return('audio' + str(upload['owner_id']) + '_' + str(upload['id']))
        
    def stats(self):
        return {}


class texttospeech:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.attachments = []
        self.busy = False

    def achievements(self):
        return {}

    def actions(self):
        return [self.action]

    def help(self):
        return ['Команда "карбот озвучь" и прикреплённое сообщение с текстом озвучит его и отправит как аудиозапись']
    
    def action(self, event):
        if self.core.uacc:
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    if event.message.text.lower() == "карбот озвучь":
                        if 'reply_message' in event.raw['object']['message'].keys():
                            text = self.parsereply(event.raw['object']['message']['reply_message'])
                            if text:
                                user = self.core.vk_session.method('users.get',{'user_id' : event.raw['object']['message']['from_id']})[0]
                                att = self.work(text, user)
                                self.core.vk.messages.send(message='Наслаждайтесь!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment=att)
                        elif len(event.raw['object']['message']['fwd_messages']):
                            text = self.parsefwd(event.raw['object']['message']['fwd_messages'])
                            user = self.core.vk_session.method('users.get',{'user_id' : event.raw['object']['message']['from_id']})[0]
                            att = self.work(text, user)
                            self.core.vk.messages.send(message='Наслаждайтесь!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment=att)

    def parsereply(self, obj):
        return self.parse_in(obj)

    def parsefwd(self, obj):
        ans = ''
        if len(obj):
            for subobj in obj:
                ans += self.parse_in(subobj) + '\n'
        return ans

    def parse_in(self, obj):
        ans = ''
        if 'reply_message' in obj.keys():
            ans += self.parse_in(obj['reply_message']) + '\n'
        if 'fwd_messages' in obj.keys():
            for subobj in obj['fwd_messages']:
                ans += self.parse_in(subobj) + '\n'
        if 'text' in obj.keys():
            if len(obj['text']) > 0:
                ans += obj['text'] + '\n'
        return ans

    def work(self, text, user):
        fname = 'speech' + str(random.randint(0, 100)) + '.mp3'
        gTTS(text, lang='ru').save(fname)
        title = "title"
        if len(text) > 200:
            title = text[:200]
        else:
            title = text
        upload = self.core.uupload.audio(fname, user['first_name'] + ' ' + user['last_name'], title)
        return('audio' + str(upload['owner_id']) + '_' + str(upload['id']))
        
    def stats(self):
        return {}








class stickers:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms

    def achievements(self):
        return {'klubn':{'text':'Вы в клубничках!','img':'ach_klub.jpg','desc':'Отправить стикер с клубничкой','params':{'state':False}},'spraveb':{'text':'Справебыдло!','desc':'Отправить стикер с орехом','params':{'state':False}}}

    def actions(self):
        return [self.stickers]
    
    def stickers(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                uname = str(event.message.from_id)
                if 'attach1_type' in event.raw[-2].keys():
                    if event.raw[-2]['attach1_type'] == 'sticker':
                        if event.raw[-2]['attach1'] == '145':
                            self.gparms['is_ach_on_user']('klubn',uname)
                            self.gparms['achieve']('klubn',uname)
                            self.gparms['is_stat_on_user']('klubn_count',uname)
                            self.gparms['stats'][uname]['klubn_count']['value'] += 1
                        if event.raw[-2]['attach1'] == '163':
                            self.gparms['is_ach_on_user']('spraveb',uname)
                            self.gparms['achieve']('spraveb',uname)
                            self.gparms['is_stat_on_user']('spraveb_count',uname)
                            self.gparms['stats'][uname]['spraveb_count']['value'] += 1

    def stats(self):
        return {'klubn_count':{'text':'Количество отправленных клубничек','params':{'value':0}},'spraveb_count':{'text':'Количество отправленных орехов','params':{'value':0}}}

    def help(self):
        return ['Считать стикеры с клубничками и орехами (отображаются в статистике)']





class bassboost:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.acting = False

    def achievements(self):
        return {}

    def actions(self):
        return [self.bassboost]
    
    def bassboost(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if 'attach1_type' in event.raw[-2].keys():
                    if event.raw[-2]['attach1_type'] == 'audio':
                        text_words = event.message.text.lower().split()
                        if text_words[0] == 'карбот' and text_words[1] == 'басы':
                            if self.acting:
                                self.core.send_message('Я ещё не забассбустил предыдущий трек, пришли чуть позже',chat_id=event.chat_id,forward_messages=None)
                            else:
                                self.acting = True
                                if len(text_words) > 2:
                                    if text_words[2].isdigit():
                                        accentuate_db = int(text_words[2])
                                    else:
                                        accentuate_db = 50
                                else:
                                    accentuate_db = 50
                                print('start')
                                mdata = event.raw[-2]['attach1'].split('_')
                                print('rawdata: ',mdata)
                                error = False
                                try:
                                    data = self.core.audio.get_audio_by_id(int(mdata[0]), int(mdata[1]))
                                except Exception as e:
                                    print('error', e)
                                    error = True
                                if not error:
                                    self.core.send_message('Ща забассбустим! Множитель - ' + str(accentuate_db),chat_id=event.chat_id,forward_messages=None)
                                    print('data: ', data)
                                    r = requests.get(data[0]['url'])
                                    with open('audio.mp3', 'wb') as output_file:
                                        output_file.write(r.content)
                                    print('file is written')
                                    attenuate_db = 0
                                    audiodata = AudioSegment.from_mp3('audio.mp3')
                                    print('file is read')
                                    audiodata_samples = audiodata.get_array_of_samples()
                                    sample_track = list(audiodata_samples)
                                    est_mean = np.mean(sample_track)
                                    est_std = 3 * np.std(sample_track) / (math.sqrt(2))
                                    bass_factor = int(round((est_std - est_mean) * 0.005))
                                    filtered = audiodata.low_pass_filter(bass_factor)
                                    combined = (audiodata - attenuate_db).overlay(filtered + accentuate_db)
                                    print('ready to write')
                                    combined.export('audio_export.mp3', format="mp3")
                                    print('written, upload')
                                    upload = self.core.upload.audio('audio_export.mp3', data[0]["artist"], data[0]["title"] + ' (bassboosted)')
                                    print('uploaded: ', upload)
                                    self.core.vk.messages.send(message='Наслаждайтесь!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='audio' + str(upload['owner_id']) + '_' + str(upload['id']))
                                else:
                                    self.core.send_message('Нет доступа, вы обосрались.',chat_id=event.chat_id,forward_messages=None)   
                                self.acting = False
    def stats(self):
        return {}


class achievements_list:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms

    def achievements(self):
        return {}

    def stats(self):
        return {}

    def actions(self):
        return [self.achievements_list, self.all_achievements]
    
    def achievements_list(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                #if self.gparms['botname'] == event.message.text[:len(self.gparms['botname'])]:
                    #if 'ачивки' == event.message.text[len(self.gparms['botname']) + 1:len(self.gparms['botname']) + 2 + len('ачивки')].lower():
                if event.message.text.lower() == 'карбот ачивки':
                    uname = str(event.message.from_id)
                    achievements = []
                    if uname in self.gparms['achievements'].keys():
                        for ach in self.gparms['achievements_original']:
                            self.gparms['is_ach_on_user'](ach,uname)
                            if self.gparms['achievements'][uname][ach]['state']:
                                achievements.append(str(self.gparms['achievements_original'][ach]['text']))
                    self.core.send_message('Ваши ачивки - ' + str(len(achievements)) + '/' + str(self.gparms['ach_len']) + ':\n- ' + '\n- '.join(achievements),chat_id=event.chat_id,forward_messages=None)
                #if 'статы' == event.message.text[len(self.gparms['botname']) + 1:len(self.gparms['botname']) + 2 + len('статы')].lower():
                if event.message.text.lower() == 'карбот статы':
                    uname = str(event.message.from_id)
                    stats = []
                    for stat in self.gparms['stats_original']:
                        self.gparms['is_stat_on_user'](stat,uname)
                        stats.append(str(self.gparms['stats_original'][stat]['text']) + ':\t' + str(self.gparms['stats'][uname][stat]['value']))
                        self.core.send_message('Ваши статы:\n- ' + '\n- '.join(stats),chat_id=event.chat_id,forward_messages=None)

    def all_achievements(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                #if self.gparms['botname'] == event.message.text[:len(self.gparms['botname'])]:
                    #if 'все ачивки' == event.message.text[len(self.gparms['botname']) + 1:len(self.gparms['botname']) + 2 + len('все ачивки')].lower():
                if event.message.text.lower() == 'карбот все ачивки':
                    text = ''
                    for ach in self.gparms['achievements_original']:
                        text += '- ' + self.gparms['achievements_original'][ach]['text'] + ': ' + self.gparms['achievements_original'][ach]['desc'] + '\n'
                    self.core.send_message('Доступные ачивки - ' + str(len(self.gparms['achievements_original'])) + ':\n' + text,chat_id=event.chat_id,forward_messages=None)

    def help(self):
        return ['Команда "карбот ачивки" покажет полученные вами ачивки', 'Команда "карбот все ачивки" покажет все доступные ачивки', 'Команда "карбот статы" отображает ваши статистики']




class jirniy:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.time = {'jir':0,'durka':0,'okurok':0,'dapizda':0,'pidocat':0}
        self.finding = [
            {
                'text': ['2 рубл', 'окурок', 'окурк'],
                'img': ['okurok.jpg'],
                'time': 0
            },
            {
                'text': ['всем привет'],
                'img': ['priv.jpg'],
                'time': 0
            },
            {
                'text': ['всем пока'],
                'img': ['okurok.jpg'],
                'time': 0
            },
            {
                'text': ['poka'],
                'img': ['okurok.jpg'],
                'time': 0
            },
            {
                'text': ['пидор'],
                'img': ['pidocat.jpg'],
                'time': 0
            },
            {
                'text': ['похуй'],
                'img': ['poh' + str(i) + '.jpg' for i in range(1,7)],
                'time': 0
            },
            {
                'text': ['питер', 'петербург', 'спб'],
                'img': ['piter.jpg'],
                'time': 0
            },
            {
                'text': ['болот'],
                'img': ['okurok.jpg'],
                'time': 0
            },
            {
                'text': ['винишк'],
                'img': ['vinishko.jpg'],
                'time': 0
            },
            {
                'text': ['русск'],
                'img': ['russ' + str(i) + '.jpg' for i in range(1,12)],
                'time': 0
            },
            {
                'text': ['салам'],
                'img': ['salam.jpg'],
                'time': 0
            },
            {
                'text': ['котлет'],
                'img': ['kotlet.jpg'],
                'time': 0
            }
        ]

    def actions(self):
        #return [self.jirniy, self.durka, self.okurok, self.dapizda, self.privet, self.pidocat, self.korona, self.zabiv, self.nebuhtet, self.poh, self.piter, self.boloto, self.vinishko]
        #return [self.dapizda, self.privet, self.nebuhtet, self.poh, self.vinishko]
        return [self.dapizda, self.korona, self.zabiv, self.nebuhtet, self.onfind]
    def stats(self):
        return {}

    def achievements(self):
        return {}
    
    def is_chat(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                return True
    
    def cooldown(self, p):
        curtime = int(time.time())
        if self.time[p] < curtime:
            self.time[p] =  curtime + 10
            return True
        else:
            return False

    '''
    def jirniy(self, event):
        if self.is_chat(event):
            if event.message.text.lower().find('жирн') != -1:
                if len(event.message.text) > 15:
                    if self.cooldown('jir'):
                        upload = self.core.upload.photo_messages('jir.jpg')[0]
                        self.core.vk.messages.send(message='Я здесь жирный!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
    
    def durka(self, event):
        if self.is_chat(event):
            if event.message.text.lower().find('дурк') != -1:
                if len(event.message.text) > 15:
                    if self.cooldown('durka'):
                        upload = self.core.upload.photo_messages('d' + str(random.randint(1, 4)) + '.jpg')[0]
                        self.core.vk.messages.send(message='Ты как блять за окно выбрался?', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
    '''

    def dapizda(self, event):
        if self.is_chat(event):
            if event.message.text.lower() == "да":
                upload = self.core.upload.photo_messages(str(Path('imgs/da' + str(random.randint(1, 20)) + '.jpg')))[0]
                self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
                                          
    def korona(self, event):
        if self.is_chat(event):
            if event.message.text.lower().find('коронавирус') != -1:
                self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='video379124050_456239018')

    def zabiv(self, event):
        if self.is_chat(event):
            if event.message.text.lower().find('забив') != -1:
                self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='video379124050_456239019')

    def nebuhtet(self, event):
        if self.is_chat(event):
            words = event.message.text.lower().split()
            if len(words) > 3:
                if words[0] == 'ну' and words[2] == 'и' and words[1] == words[3]:
                    upload = self.core.upload.photo_messages(str(Path('imgs/nebuhtet.jpg')))[0]
                    self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))

    def onfind(self, event):
        msgtext = event.message.text.lower()
        for el in self.finding:
            curtime = int(time.time())
            if el['time'] + 60 * 1 < curtime:
                for eltext in el['text']:
                    if msgtext.find(eltext) != -1:
                        upload = self.core.upload.photo_messages(str(Path('imgs/' + random.choice(el['img']))))[0]
                        self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=None,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
                        el['time'] =  curtime
                        break



    def help(self):
        return ['Бот реагирует картинкой или роликом на некоторые определённые фразы']
      

class pomyanem:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms

    def actions(self):
        return [self.pomyanem]
        
    def achievements(self):
        return {}

    def stats(self):
        return {}
    
    def pomyanem(self, event):
        if event.type_id == 8:
            upload = self.core.upload.photo_messages('dosvyazi.jpg')[0]
            self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
        if event.type_id == 7:
            upload = self.core.upload.photo_messages('dosvyazi.jpg')[0]
            self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))

    def help(self):
        return ['Бот реагирует на выход из беседы']

class when_join:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms

    def actions(self):
        return [self.when_join]
        
    def achievements(self):
        return {}

    def stats(self):
        return {}
    
    def when_join(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.message.from_id != 379124050:
                    if event.message.text.lower() == "карбот вступление":
                        vals = self.core.vk_session.method('messages.getConversationMembers', {'peer_id': event.chat_id + 2000000000})
                        val = next(item for item in vals['items'] if item['member_id'] == event.message.from_id)
                        date = datetime.datetime.fromtimestamp(val['join_date'])
                        self.core.send_message('Вы вступили в беседу ' + date.strftime('%Y-%m-%d %H:%M:%S'),chat_id=event.chat_id,forward_messages=None)

    def help(self):
        return ['Команда "карбот вступление" покажет дату последнего вступления отправившего её пользователя в беседу']

class quotes:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.f = open('quotes.txt', 'r', encoding="utf8")
        self.quotes = self.f.readlines()
        self.times = []
        self.trigtime = 0

    def actions(self):
        return [self.quoting]
        
    def achievements(self):
        return {}

    def stats(self):
        return {}

    def quoting(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.message.from_id != 379124050:
                    if len(event.message.text) > 0:
                        curtime = int(time.time())
                        for i_time in self.times:
                            if i_time + 300 < curtime:
                                self.times.remove(i_time)
                        self.times.append(curtime)
                        words = event.message.text.lower().split()
                        is_called = False
                        if words[0] == 'карбот' and words[1] == 'цитата':
                            words = words[2:]
                            is_called = True
                        if (len(self.times) > 50 and curtime > self.trigtime + 120) or is_called:
                            random.shuffle(self.quotes)
                            is_found = False
                            while len(words):
                                word = random.choice(words)
                                words.remove(word)
                                if len(word) > 5:
                                    word = word[0:-2]
                                quote = [q for q in self.quotes if q.lower().find(word) != -1]
                                if len(quote):
                                    is_found = True
                                    quote = random.choice(quote)
                                    break
                            if not is_found:
                                quote = random.choice(self.quotes)
                            self.core.send_message(quote,chat_id=event.chat_id,forward_messages=None)
                            self.trigtime = curtime

    def help(self):
        return ['Команда "карбот цитата" вернёт случайную цитату из своей библиотеки, можно дописать слова для поиска']


class ban_new_user:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.newfags = []
        self.newfags_time = []
        self.newfags_state = []
        self.isrun = False
        

    class newfag:
        def __init__(self, core, gparms, id, time):
            self.core = core
            self.gparms = gparms
            self.sleep1 = 150
            self.sleep2 = 150
            self.id = id
            self.idc = id
            self.time = time
            self.zerosent = False
            self.sent = False
            self.rm = False
            self.thread = Thread(target=self.proc)
            self.thread.start()

        def proc(self):
            time.sleep(self.sleep1)
            if self.id:
                self.core.send_message('@id' + str(self.idc) + '(' + self.core.vk_session.method('users.get',{'user_id' : self.idc})[0]['first_name'] + '), вы всё ещё ничего не написали в беседе, это чревато баном.',chat_id=event.chat_id)
                time.sleep(self.sleep2)
                if self.id:
                    print('user rm: ', self.id)
                    self.id = 0
                    self.core.remove_user(event.chat_id, self.idc)
                    self.core.send_message('@id' + str(self.idc) + '(' + self.core.vk_session.method('users.get',{'user_id' : self.idc})[0]['first_name'] + '), бан!',chat_id=event.chat_id)
            self.rm = True

    def actions(self):
        return [self.ban_new_user]
    
    def achievements(self):
        return {}

    def stats(self):
        return {}
    
    def ban_new_user(self, event):
        self.clean()

        if event.type_id == 6:
            print('user added: ', event.info['user_id'])
            self.newfags.append(self.newfag(self.core, self.gparms, event.info['user_id'], int(time.time())))
            self.core.send_message('@id' + str(event.info['user_id']) + '(' + self.core.vk_session.method('users.get',{'user_id' : event.info['user_id']})[0]['first_name'] + '), добро пожаловать в беседу!\nНе забудьте отправить сообщению в беседу, чтобы мы удостоверились, что вы не бот, и не забанили вас.',chat_id=event.chat_id)
        
        elif (event.type_id == 8 or event.type_id == 7):
            print('user gone0: ', event.info['user_id'])
            for newfag in self.newfags:
                if event.info['user_id'] == newfag.id:
                    print('user gone: ', event.info['user_id'])
                    newfag.id = 0
                    self.core.send_message('@id' + str(newfag.idc) + '(' + self.core.vk_session.method('users.get',{'user_id' : newfag.idc})[0]['first_name'] + ') преждевременно покинул(а) нас.',chat_id=event.chat_id)
                    break
        
        elif event.type == VkBotEventType.MESSAGE_NEW:
            time.sleep(1)
            if event.from_chat:
                #print('msg:', event.message.text)
                for newfag in self.newfags:
                    if event.message.from_id == newfag.id:
                        print('msg:', event.message.text)
                        if newfag.zerosent:
                            newfag.id = 0
                            print('user ready: ', event.message.from_id)
                            self.core.send_message('Добро пожаловать в беседу!',chat_id=event.chat_id,forward_messages=None)
                        else:
                            print('user not newfag: ', event.message.from_id)
                            newfag.zerosent = True
                        break
                if event.message.text.lower() == 'карбот антибан':
                    text = ''
                    if len(self.newfags):
                        for newfag in self.newfags:
                            if newfag.id:
                                text += '\n@id' + str(newfag.idc) + '(' + self.core.vk_session.method('users.get',{'user_id' : newfag.idc})[0]['first_name'] + ')'
                                newfag.id = 0
                    if len(text):
                        text = 'Автобан отменён, помилованы следующие:' + text
                    else:
                        text = 'Список претендентов на бан пуст.'
                    self.core.send_message(text,chat_id=event.chat_id)


    def clean(self):
        for newfag in self.newfags:
            if newfag.rm:
                print('user clean')
                self.newfags.remove(newfag)

    def help(self):
        return ['Бот автобанит тех, кто зашёл в беседу и не отписался в течение 5 минут', 'Команда "карбот антибан" очищает список текущих претендентов на бан из предыдущего пункта']




class ruletka:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.ruletka_is = False
        self.ruletka_list = []

    def actions(self):
        return [self.shoot, self.ruletka]

    def achievements(self):
        return {'first_ruletka':{'text':'Кто не рискует, тот не пидор','desc':'Первая игра в карательную рулетку','params':{'state':False,'count':0}},'first_ruletka_pidor':{'text':'Один раз не пидорас','desc':'Первая победа в карательной рулетке','params':{'state':False,'count':0}},'first_ruletka_call':{'text':'Спорим на пидора?','desc':'Первый вызов карательной рулетки','params':{'state':False,'count':0}},'odin_strel':{'text':'Одинокий стрелок','desc':'Не хватило игроков для запуска рулетки','params':{'state':False,'count':0}}}

    def stats(self):
        return {'ruletka_shoot':{'text':'Попыток игры в рулетку','params':{'value':0}},'ruletka_win':{'text':'Побед в рулетке','params':{'value':0}},'ruletka_start':{'text':'Запусков рулетки','params':{'value':0}}}
    
    def shoot(self, event):
        if self.ruletka_is:
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:
                    if event.message.text.lower().find('стреляй') != -1:
                        print(event.message.from_id)
                        uname = str(event.message.from_id)
                        self.gparms['is_ach_on_user']('first_ruletka',uname)
                        self.gparms['achievements'][uname]['first_ruletka']['count'] += 1
                        if self.gparms['achievements'][uname]['first_ruletka']['count'] == 1:
                            self.gparms['achieve']('first_ruletka',uname)
                        self.gparms['is_stat_on_user']('ruletka_shoot',uname)
                        self.gparms['stats'][uname]['ruletka_shoot']['value'] = self.gparms['achievements'][uname]['first_ruletka']['count']
                        name = self.core.vk_session.method('users.get',{'user_id' : event.message.from_id})[0]['first_name']
                        if event.message.from_id in self.ruletka_list:
                            self.core.send_message('@id' + str(event.message.from_id) + '(' + name + '), вы уже в игре!',chat_id=event.chat_id,forward_messages=None, delay = 2)
                        else:
                            self.ruletka_list.append(event.message.from_id)
                            self.core.send_message('@id' + str(event.message.from_id) + '(' + name + '), принято!',chat_id=event.chat_id,forward_messages=None, delay = 2)
    
    def ruletka(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.message.from_id != 379124050:
                    if event.message.text.lower().find('карбот рулетка') != -1:
                        print(dir(event))
                        print(event.obj)
                        print(event.message)
                        uname = str(event.message.from_id)
                        self.gparms['is_ach_on_user']('first_ruletka_call',uname)
                        self.gparms['achievements'][uname]['first_ruletka_call']['count'] += 1
                        if self.gparms['achievements'][uname]['first_ruletka_call']['count'] == 1:
                            self.gparms['achieve']('first_ruletka_call',uname)
                        self.gparms['is_stat_on_user']('ruletka_start',uname)
                        self.gparms['stats'][uname]['ruletka_start']['value'] = self.gparms['achievements'][uname]['first_ruletka_call']['count']
                        if self.ruletka_is:
                            self.core.send_message('Рулетка сейчас активна!',chat_id=event.chat_id,forward_messages=None, delay = 2)
                        else:
                            self.ruletka_is = True
                            self.ruletka_list.append(event.message.from_id)
                            name = self.core.vk_session.method('users.get',{'user_id' : event.message.from_id})[0]['first_name']
                            self.core.send_message('Начинаем карательную рулетку!\nЧтобы участвовать в ней, напишите "стреляй".\nУ вас есть 30 секунд для участия.\n@id' + str(event.message.from_id) + '(' + name + '), принято!',chat_id=event.chat_id,forward_messages=None, delay = 2)
                            time.sleep(10)
                            self.core.send_message('Осталось 20 секунд.',chat_id=event.chat_id, delay = 0)
                            time.sleep(10)
                            self.core.send_message('Осталось 10 секунд.',chat_id=event.chat_id, delay = 0)
                            time.sleep(5)
                            self.core.send_message('5',chat_id=event.chat_id, delay = 0)
                            time.sleep(5)
                            self.ruletka_is = False
                            if len(self.ruletka_list) > 1:
                                uid = random.choice(self.ruletka_list)
                                name = self.core.vk_session.method('users.get',{'user_id' : uid})[0]['first_name']
                                self.core.send_message('@id' + str(uid) + '(' + name + '), вы пидор!',chat_id=event.chat_id)
                                uname = str(uid)
                                self.gparms['is_ach_on_user']('first_ruletka_pidor',uname)
                                self.gparms['achievements'][uname]['first_ruletka_pidor']['count'] += 1
                                if self.gparms['achievements'][uname]['first_ruletka_pidor']['count'] == 1:
                                    self.gparms['achieve']('first_ruletka_pidor',uname)
                                self.gparms['is_stat_on_user']('ruletka_win',uname)
                                self.gparms['stats'][uname]['ruletka_win']['value'] = self.gparms['achievements'][uname]['first_ruletka_pidor']['count']
                            else:                        
                                self.core.send_message('Недостаточно игроков!',chat_id=event.chat_id)
                                self.gparms['is_ach_on_user']('odin_strel',uname)
                                self.gparms['achieve']('odin_strel',uname)
                            self.ruletka_list.clear()

    def help(self):
        return ['Команда "карбот рулетка" запускает рулетку, попробуйте!', 'Команда "стреляй" при запущенной рулетке из предыдущего пункта делает Вас её участником']


class sorbetoban:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.alphabet = [['s','S','с','С','$','ς','c','С','C','Ç','ᴄ','Ⓒ','匚','ᶜ','仁','⊂','☪','¢','《','[','Ĉ','{','Č','Ç','ℂ'],['০','o','O','о','О','0','ο','o','О','o','Ω','о́','ø','∅','ᴏ','Ⓞ','口','ᵒ','О','○','°','●','ø','[','Ø','ö'],['p','P','r','R','р','Р','ρ','p','Р','p','₽','ק','ř','р','尸','卩','ℙ','®','₱','ℙ','я','Я'],['b','B','б','Б','β','б','Б','b','ß','b','б','6','δ','右','Ҕ','Ϭ'],['e','E','е','E','ε','е','Е','e','ę','э','Э','є','Є','ᴇ','Ѣ','ъ','Ъ','Ⓔ','е́','巳','ᵉ','℮','€','£','Ē','ė','℮', '3'],['t','T','т','Т','τ','т','Т','t','ŧ','т','7','丅','丁','Т','⚚','+']]
        self.word = 'sorbet'
        self.word_len = len(self.word)
        self.word_prepare()

    def actions(self):
        return [self.word_watcher]

    def achievements(self):
        return {'first_ban':{'text':'Свой первый бан я получил в…','img':'first_ban.jpg','desc':'Получить первый бан за упоминание сорбета.','params':{'state':False,'count':0}},'5_bans':{'text':'Мелкий воришка','desc':'Получить 5 банов за сорбет.','params':{'state':False}}}

    def stats(self):
        return {'sorbetoban':{'text':'Банов за сорбет','params':{'value':0}}}

    def word_watcher(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            if event.from_chat:
                if self.word_check(event.message.text):
                    '''uname = str(event.message.from_id)
                    self.gparms['is_ach_on_user']('first_ban',uname)
                    self.gparms['is_ach_on_user']('5_bans',uname)
                    self.gparms['achievements'][uname]['first_ban']['count'] += 1
                    if self.gparms['achievements'][uname]['first_ban']['count'] == 1:
                        self.gparms['achieve']('first_ban',uname)
                    elif self.gparms['achievements'][uname]['first_ban']['count'] == 5:
                        self.gparms['achieve']('5_bans',uname)
                    self.gparms['is_stat_on_user']('sorbetoban',uname)
                    self.gparms['stats'][uname]['sorbetoban']['value'] = self.gparms['achievements'][uname]['first_ban']['count']
                    print(self.gparms['chat_admins'])'''
                    if event.message.from_id in self.gparms['chat_admins']:
                        self.name = self.core.vk_session.method('users.get',{'user_id' : event.message.from_id})[0]['first_name']
                        self.core.send_message('@id' + str(event.message.from_id) + '(' + self.name + ') помнит о том, кто нас объединил!',chat_id=event.chat_id,forward_messages=None)
                    if event.message.from_id == 373593096:
                        self.core.send_message('Андрюша, и тебе Тимошу!',chat_id=event.chat_id,forward_messages=None)
                    else:
                        self.core.send_message('И тебе сорбет!',chat_id=event.chat_id,forward_messages=None)

    def word_prepare(self):
        self.word_letters = []
        for letter in self.word:
            for alp in range(len(self.alphabet)):
                if letter in self.alphabet[alp]:
                    self.word_letters.append(alp)
                    break
            

    def word_check(self, text):
        text_len = len(text)
        letters_numb = [text_len for i in range(len(self.word))]
        letter_i = 0
        for letter in self.alphabet[self.word_letters[letter_i]]:
            curr = text.find(letter)
            if curr != -1:
                if curr < letters_numb[letter_i]:
                    letters_numb[letter_i] = curr
        if letters_numb[letter_i] == text_len:
            return False
        
        for letter_i in range(len(self.word))[1:]:
            letter_id = self.word_letters[letter_i]
            for letter in self.alphabet[letter_id]:
                curr = text.find(letter, letters_numb[letter_i - 1])
                if curr != -1:
                    if curr < letters_numb[letter_i]:
                        letters_numb[letter_i] = curr
            if letters_numb[letter_i] == text_len:
                return False
        if letters_numb[-1] - letters_numb[0] < self.word_len * 2:
            return True
        else:
            return False

    def help(self):
        return ['Бан за упоминание сорбета']

'''    
    
    
    def spina(self):
        hour_last = 0
        self.actions_add(self.spina_watcher)
        while True:
            hour = datetime.datetime.now().hour
            if hour != hour_last:
                hour_last = hour
                if hour == 6:
                    self.core.send_message('Доброе утро! Проснулись, потянулись, выпрямили спину!',chat_id=self.chat_id)
                elif hour == 0:
                    self.core.send_message('Спокойной ночи! И не забудьте выпрямиь спину!',chat_id=self.chat_id)
                else:
                    self.core.send_message('Выпрями спину!',chat_id=self.chat_id)
                time.sleep(60)
    
    def spina_watcher(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.chat_id == self.chat_id:
            if event.message.from_id != 379124050:
                if event.message.text.find('выпрямил') != -1 or event.message.text.find('Выпрямил') != -1:
                    self.core.send_message('Молодец! Не забывай продолжать держать спину прямой!',chat_id=self.chat_id,forward_messages=None)
                if event.message.text.find('Спин') != -1 or event.message.text.find('спин') != -1:
                    self.core.send_message('Спину нужно выпрямлять!',chat_id=self.chat_id,forward_messages=None)
    
    def ue_ban(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat and event.chat_id == self.chat_id:
            if event.message.from_id != 379124050:
                if event.message.text.find('бан') != -1 or event.message.text.find('Бан') != -1:
                    self.core.send_message('Уебан!',chat_id=self.chat_id,forward_messages=None)
                if event.message.text.find('бот') != -1 or event.message.text.find('Бот') != -1:
                    self.core.send_message('Уебот!',chat_id=self.chat_id,forward_messages=None)
'''

with open('config.json', 'r') as f:
        conf = json.load(f)

