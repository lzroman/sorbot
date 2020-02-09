#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
from sorbot_core import sorbot_core
from vk_api.longpoll import VkChatEventType, VkEventType
import time, random
from threading import Thread
import datetime
import json

#import discord



class sorbot:
    def __init__(self, token, chat_id, botname, admin_ids):
        self.core = sorbot_core(token)
        self.chat_id = chat_id
        self.admin_ids = admin_ids
        self.botname = botname.lower()
        self.plugins = []
        self.plugins_run = []
        self.actions = []
        self.threads = []
        self.admin_list = []
        self.get_admins()
        self.gparms = {'chat_id': self.chat_id, 'botname': self.botname, 'chat_admins': self.admin_list, 'achievements': {}, 'achievements_original': {}, 'ach_len': 0, 'stats_original': {}, 'stats': {}}
        with open('achievements.json', 'r') as f:
            self.gparms['achievements'] = json.load(f)
        with open('stats.json', 'r') as f:
            self.gparms['stats'] = json.load(f)
        self.gparms['is_ach_on_user'] = self.is_ach_on_user
        self.gparms['achieve'] = self.achieve
        self.gparms['is_stat_on_user'] = self.is_stat_on_user
        self.predlojka = Thread(target=self.check_suggestions)
        self.predlojka.start()
        self.saving_ach_thread = Thread(target=self.saving_ach)
        self.saving_ach_thread.start()
        self.achieve_thread_onject = Thread()


    def check_suggestions(self):
        #189945062 - test
        #137996395 - kk
        group_id = 137996395
        self.core.get_news_suggested(group_id, 'imgs\\wm_kk.png')
        while True:
            time.sleep(10000)
            self.core.get_news_suggested(group_id, 'imgs\\wm_kk.png')

    def get_admins(self):
        self.admin_list.clear()
        ans = self.core.vk_session.method('messages.getConversationMembers',{'peer_id' : self.chat_id + 2000000000})
        for user in ans['items']:
            if 'is_admin' in user:
                if user['is_admin']:
                    self.admin_list.append(user['member_id'])
        print(self.admin_list)

    
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
                break

    def saving_ach(self):
        time.sleep(600)
        while True:
            with open('achievements.json', 'w') as outfile:
                json.dump(self.gparms['achievements'], outfile)
            with open('stats.json', 'w') as outfile:
                json.dump(self.gparms['stats'], outfile)
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
            for action in plugin.actions():
                self.actions.append(action)
        self.gparms['ach_len'] = len(self.gparms['achievements_original'])
        while True:
            events = self.core.getevents()
            for event in events:
                for action in self.actions:
                    self.threads.append(Thread(target=self.execute_action,args=(action,event)))
                    self.threads[-1].start()
            for thread in self.threads:
                if not thread.is_alive():
                    self.threads.remove(thread)
            events.clear()

    def achieve(self, ach, user):
        self.achieve_thread_onject = Thread(target=self.achieve_thread,args=(ach,str(user)))
        self.achieve_thread_onject.start()

    def achieve_thread(self, ach, user):
        if not self.gparms['achievements'][user][ach]['state']:
            self.gparms['achievements'][user][ach]['state'] = True
            if 'img' in self.gparms['achievements_original'][ach]:
                upload = self.core.upload.photo_messages('ach_img\\' + self.gparms['achievements_original'][ach]['img'])[0]
                time.sleep(5)
                self.core.vk.messages.send(message='@id' + str(user) + '(' + self.core.vk_session.method('users.get',{'user_id' : user})[0]['first_name'] + '), вы получили новое достижение - "' + self.gparms['achievements_original'][ach]['text'] + '"!\n' + self.gparms['achievements_original'][ach]['desc'],chat_id=self.gparms['chat_id'], random_id=vk_api.utils.get_random_id(),attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
            else:
                self.core.send_message('@id' + str(user) + '(' + self.core.vk_session.method('users.get',{'user_id' : user})[0]['first_name'] + '), вы получили новое достижение - "' + self.gparms['achievements_original'][ach]['text'] + '"!\n' + self.gparms['achievements_original'][ach]['desc'],chat_id=self.gparms['chat_id'])

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
            pass
    
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
        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id == self.gparms['chat_id']:
                    #if self.gparms['botname'] == event.text[:len(self.gparms['botname'])]:
                        #if 'ачивки' == event.text[len(self.gparms['botname']) + 1:len(self.gparms['botname']) + 2 + len('ачивки')].lower():
                    if event.text.lower() == 'карбот ачивки':
                        uname = str(event.user_id)
                        achievements = []
                        if uname in self.gparms['achievements'].keys():
                            for ach in self.gparms['achievements_original']:
                                self.gparms['is_ach_on_user'](ach,uname)
                                if self.gparms['achievements'][uname][ach]['state']:
                                    achievements.append(str(self.gparms['achievements_original'][ach]['text']))
                        self.core.send_message('Ваши ачивки - ' + str(len(achievements)) + '/' + str(self.gparms['ach_len']) + ':\n- ' + '\n- '.join(achievements),chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                    #if 'статы' == event.text[len(self.gparms['botname']) + 1:len(self.gparms['botname']) + 2 + len('статы')].lower():
                    if event.text.lower() == 'карбот статы':
                        uname = str(event.user_id)
                        stats = []
                        for stat in self.gparms['stats_original']:
                            self.gparms['is_stat_on_user'](stat,uname)
                            stats.append(str(self.gparms['stats_original'][stat]['text']) + ':\t' + str(self.gparms['stats'][uname][stat]['value']))
                        self.core.send_message('Ваши статы:\n- ' + '\n- '.join(stats),chat_id=self.gparms['chat_id'],forward_messages=event.message_id)

    def all_achievements(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id == self.gparms['chat_id']:
                    #if self.gparms['botname'] == event.text[:len(self.gparms['botname'])]:
                        #if 'все ачивки' == event.text[len(self.gparms['botname']) + 1:len(self.gparms['botname']) + 2 + len('все ачивки')].lower():
                    if event.text.lower() == 'карбот все ачивки':
                        text = ''
                        for ach in self.gparms['achievements_original']:
                            text += '- ' + self.gparms['achievements_original'][ach]['text'] + ': ' + self.gparms['achievements_original'][ach]['desc'] + '\n'
                        self.core.send_message('Доступные ачивки - ' + str(len(self.gparms['achievements_original'])) + ':\n' + text,chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
 

                    


class jirniy:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.time = {'jir':0,'durka':0,'okurok':0,'dapizda':0}

    def actions(self):
        return [self.jirniy, self.durka, self.okurok, self.dapizda]
        
    def stats(self):
        return {}

    def achievements(self):
        return {}
    
    def is_chat(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.user_id != 379124050:
                    return event.chat_id == self.gparms['chat_id']
    
    def cooldown(self, p):
        curtime = int(time.time())
        if self.time[p] < curtime:
            self.time[p] =  curtime + 600
            return True
        else:
            return False

    
    def jirniy(self, event):
        if self.is_chat(event):
            if event.text.lower().find('жирн') != -1:
                if len(event.text) > 15:
                    if self.cooldown('jir'):
                        upload = self.core.upload.photo_messages('imgs\\jir.jpg')[0]
                        time.sleep(1)
                        self.core.vk.messages.send(message='Я здесь жирный!', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=event.message_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
    
    def durka(self, event):
        if self.is_chat(event):
            if event.text.lower().find('дурк') != -1:
                if len(event.text) > 15:
                    if self.cooldown('durka'):
                        upload = self.core.upload.photo_messages('imgs\\d' + str(random.randint(1, 4)) + '.jpg')[0]
                        time.sleep(1)
                        self.core.vk.messages.send(message='Ты как блять за окно выбрался?', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=event.message_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))

    def okurok(self, event):
        if self.is_chat(event):
            if event.text.find('2 рубл') != -1 or event.text.lower().find('окурок') != -1 or event.text.lower().find('окурк') != -1:
                if self.cooldown('okurok'):
                    upload = self.core.upload.photo_messages('imgs\\okurok.jpg')[0]
                    time.sleep(1)
                    self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=event.message_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))
                        
    def dapizda(self, event):
        if self.is_chat(event):
            if event.text.lower() == "да":
                if self.cooldown('dapizda'):
                    upload = self.core.upload.photo_messages('imgs\\da.jpg')[0]
                    time.sleep(1)
                    self.core.vk.messages.send(message='', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=event.message_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))



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
        if event.type_id == 8 and event.chat_id == self.gparms['chat_id']:
            self.core.send_message('Помянем.',chat_id=self.gparms['chat_id'])
        if event.type_id == 7 and event.chat_id == self.gparms['chat_id']:
            self.core.send_message('Помянем.',chat_id=self.gparms['chat_id'])



class ban_new_user:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.newfags = []
        self.newfags_time = []
        self.newfags_state = []

    def actions(self):
        return [self.ban_new_user]
    
    def achievements(self):
        return {}

    def stats(self):
        return {}
    
    def ban_new_user(self, event):
        if event.type_id == 6 and event.chat_id == self.gparms['chat_id']:
            self.newfags.append(event.info['user_id'])
            self.newfags_time.append(int(time.time()))
            self.newfags_state.append(0)
            self.core.send_message('@id' + str(event.info['user_id']) + '(' + self.core.vk_session.method('users.get',{'user_id' : event.info['user_id']})[0]['first_name'] + '), добро пожаловать в беседу каркула!\nНе забудьте отписаться, чтобы мы удостоверились, что вы не бот, и не забанили вас.',chat_id=self.gparms['chat_id'])
        elif event.type == VkEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id == self.gparms['chat_id']:
                    if event.user_id in self.newfags:
                        ind = self.newfags.index(event.user_id)
                        if self.newfags_state[ind] == 0:
                            self.newfags_state[ind] = 1
                        else:
                            ind = self.newfags.index(event.user_id)
                            self.newfags.pop(ind)
                            self.newfags_time.pop(ind)
                            self.newfags_state.pop(ind)
                            self.core.send_message('Теперь вы - полноценный гвардеец @smayanezikom (Карательной кулинарии), поздравляем!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
        curtime = int(time.time())
        for ind in range(len(self.newfags)):
            if self.newfags_state[ind] == 1:
                if curtime - self.newfags_time[ind] > 120:
                    self.core.send_message('@id' + str(self.newfags[ind]) + '(' + self.core.vk_session.method('users.get',{'user_id' : self.newfags[ind]})[0]['first_name'] + '), вы всё ещё ничего не написали в беседе, это чревато баном.',chat_id=self.gparms['chat_id'])
                    self.newfags_state[ind] = 2
            else:
                if curtime - self.newfags_time[ind] > 300:
                    self.core.remove_user(self.gparms['chat_id'], self.newfags[ind])
                    self.newfags.pop(ind)
                    self.newfags_time.pop(ind)
                    self.newfags_state.pop(ind)


class ruletka:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.ruletka_is = False
        self.ruletka_list = []

    def actions(self):
        return [self.shoot, self.ruletka]

    def achievements(self):
        return {'first_ruletka':{'text':'Кто не рискует, тот не пидор','desc':'Первая игра в карательную рулетку','params':{'state':False,'count':0}},'first_ruletka_pidor':{'text':'Один раз не пидорас','desc':'Первая победа в карательной рулетке','params':{'state':False,'count':0}},'first_ruletka_call':{'text':'Спорим на пидора?','desc':'Первый вызов карательной рулетки','params':{'state':False,'count':0}}}

    def stats(self):
        return {'ruletka_shoot':{'text':'Попыток игры в рулетку','params':{'value':0}},'ruletka_win':{'text':'Побед в рулетке','params':{'value':0}},'ruletka_start':{'text':'Запусков рулетки','params':{'value':0}}}
    
    def shoot(self, event):
        if self.ruletka_is:
            if event.type == VkEventType.MESSAGE_NEW:
                if event.from_chat:
                    if event.chat_id == self.gparms['chat_id']:
                        if event.text.lower() == 'стреляй':
                            uname = str(event.user_id)
                            self.gparms['is_ach_on_user']('first_ruletka',uname)
                            self.gparms['achievements'][uname]['first_ruletka']['count'] += 1
                            if self.gparms['achievements'][uname]['first_ruletka']['count'] == 1:
                                self.gparms['achieve']('first_ruletka',uname)
                            self.gparms['is_stat_on_user']('ruletka_shoot',uname)
                            self.gparms['stats'][uname]['ruletka_shoot']['value'] = self.gparms['achievements'][uname]['first_ruletka']['count']
                            if event.user_id in self.ruletka_list:
                                self.core.send_message('Вы уже в игре!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id, delay = 2)
                            else:
                                self.ruletka_list.append(event.user_id)
                                self.core.send_message('Принято!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id, delay = 2)
    
    def ruletka(self, event):
        if event.type == VkEventType.MESSAGE_NEW:
            if event.from_chat:
                if event.chat_id == self.gparms['chat_id']:
                    if event.text.lower() == 'карбот рулетка':
                        uname = str(event.user_id)
                        self.gparms['is_ach_on_user']('first_ruletka_call',uname)
                        self.gparms['achievements'][uname]['first_ruletka_call']['count'] += 1
                        if self.gparms['achievements'][uname]['first_ruletka_call']['count'] == 1:
                            self.gparms['achieve']('first_ruletka_call',uname)
                        self.gparms['is_stat_on_user']('ruletka_start',uname)
                        self.gparms['stats'][uname]['ruletka_start']['value'] = self.gparms['achievements'][uname]['first_ruletka_call']['count']
                        if self.ruletka_is:
                            self.core.send_message('Рулетка сейчас активна!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id, delay = 2)
                        else:
                            self.ruletka_is = True
                            self.core.send_message('Начинаем карательную рулетку!\nЧтобы участвовать в ней, напишите "стреляй".\nУ вас есть 30 секунд для участия.',chat_id=self.gparms['chat_id'],forward_messages=event.message_id, delay = 2)
                            time.sleep(10)
                            self.core.send_message('Осталось 20 секунд.',chat_id=self.gparms['chat_id'], delay = 0)
                            time.sleep(10)
                            self.core.send_message('Осталось 10 секунд.',chat_id=self.gparms['chat_id'], delay = 0)
                            time.sleep(5)
                            self.core.send_message('5',chat_id=self.gparms['chat_id'], delay = 0)
                            time.sleep(5)
                            self.core.send_message('И победителем становится…',chat_id=self.gparms['chat_id'], delay = 0)
                            if len(self.ruletka_list) > 1:
                                uid = random.choice(self.ruletka_list)
                                name = self.core.vk_session.method('users.get',{'user_id' : uid})[0]['first_name']
                                self.core.send_message('@id' + str(uid) + '(' + name + '), вы пидор!',chat_id=self.gparms['chat_id'])
                                uname = str(uid)
                                self.gparms['is_ach_on_user']('first_ruletka_pidor',uname)
                                self.gparms['achievements'][uname]['first_ruletka_pidor']['count'] += 1
                                if self.gparms['achievements'][uname]['first_ruletka_pidor']['count'] == 1:
                                    self.gparms['achieve']('first_ruletka_pidor',uname)
                                self.gparms['is_stat_on_user']('ruletka_win',uname)
                                self.gparms['stats'][uname]['ruletka_win']['value'] = self.gparms['achievements'][uname]['first_ruletka_pidor']['count']
                            else:                        
                                self.core.send_message('Недостаточно игроков!',chat_id=self.gparms['chat_id'])
                            self.ruletka_is = False
                            self.ruletka_list.clear()


class sorbetoban:
    def __init__(self, core, gparms):
        self.core = core
        self.gparms = gparms
        self.alphabet = [['s','S','с','С','$','ς','c','С','C','Ç','ᴄ','Ⓒ','匚','ᶜ','仁','⊂','☪','¢','《','[','Ĉ','{','Č','Ç','ℂ'],['০','o','O','о','О','0','ο','o','О','o','Ω','о́','ø','∅','ᴏ','Ⓞ','口','ᵒ','О','○','°','●','ø','[','Ø','ö'],['p','P','r','R','р','Р','ρ','p','Р','p','₽','ק','ř','р','尸','卩','ℙ','®','₱','ℙ'],['b','B','б','Б','β','б','Б','b','ß','b','б','6','δ','右','Ҕ','Ϭ'],['e','E','е','E','ε','е','Е','e','ę','э','Э','є','Є','ᴇ','Ѣ','ъ','Ъ','Ⓔ','е́','巳','ᵉ','℮','€','£','Ē','ė','℮'],['t','T','т','Т','τ','т','Т','t','ŧ','т','7','丅','丁','Т','⚚']]
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
        if event.type == VkEventType.MESSAGE_NEW and event.from_chat and event.chat_id == self.gparms['chat_id']:
            if self.word_check(event.text):
                if event.user_id != 379124050:
                    uname = str(event.user_id)
                    self.gparms['is_ach_on_user']('5_bans',uname)
                    self.gparms['achievements'][uname]['first_ban']['count'] += 1
                    if self.gparms['achievements'][uname]['first_ban']['count'] == 1:
                        self.gparms['achieve']('first_ban',uname)
                    elif self.gparms['achievements'][uname]['first_ban']['count'] == 5:
                        self.gparms['achieve']('5_bans',uname)
                    self.gparms['is_stat_on_user']('sorbetoban',uname)
                    self.gparms['stats'][uname]['sorbetoban']['value'] = self.gparms['achievements'][uname]['first_ban']['count']
                    if event.user_id in self.gparms['chat_admins']:
                        if event.user_id == self.gparms['chat_admins'][0]:
                            self.core.send_message('Привет, Кеса! Хвала Священному Сорбету!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                        else:
                            self.core.send_message('Всегда на страже сорбетопорядка!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                    elif event.user_id == 373593096:
                        self.core.send_message('Андрюша, а тебе не бан.',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                    else:
                        self.core.send_message('Бан!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                    '''
                    else:
                        if event.user_id in [277183894,174005550]:
                            self.core.send_message('Благодарим за помощь в становлении сорбетной гвардии!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                        else:
                            self.core.send_message('Бан!',chat_id=self.gparms['chat_id'],forward_messages=event.message_id)
                    '''

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
        if letters_numb[-1] - letters_numb[0] < self.word_len * 3:
            return True
        else:
            return False

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
        if event.type == VkEventType.MESSAGE_NEW and event.from_chat and event.chat_id == self.chat_id:
            if event.user_id != 379124050:
                if event.text.find('выпрямил') != -1 or event.text.find('Выпрямил') != -1:
                    self.core.send_message('Молодец! Не забывай продолжать держать спину прямой!',chat_id=self.chat_id,forward_messages=event.message_id)
                if event.text.find('Спин') != -1 or event.text.find('спин') != -1:
                    self.core.send_message('Спину нужно выпрямлять!',chat_id=self.chat_id,forward_messages=event.message_id)
    
    def ue_ban(self, event):
        if event.type == VkEventType.MESSAGE_NEW and event.from_chat and event.chat_id == self.chat_id:
            if event.user_id != 379124050:
                if event.text.find('бан') != -1 or event.text.find('Бан') != -1:
                    self.core.send_message('Уебан!',chat_id=self.chat_id,forward_messages=event.message_id)
                if event.text.find('бот') != -1 or event.text.find('Бот') != -1:
                    self.core.send_message('Уебот!',chat_id=self.chat_id,forward_messages=event.message_id)
'''
with open('config.json', 'r') as f:
        conf = json.load(f)

bot = sorbot(conf['token'], conf['chat_id'], conf['botname'], conf['admin_ids'])
bot.plugins_add(jirniy)
bot.plugins_add(pomyanem)
bot.plugins_add(ban_new_user)
bot.plugins_add(ruletka)
bot.plugins_add(sorbetoban)
bot.plugins_add(achievements_list)
bot.start()
