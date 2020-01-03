#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
import vk_core
from vk_api.longpoll import VkChatEventType, VkEventType
import time, random
from threading import Thread
import datetime

import discord



class karbot:
    def __init__(self):
        vktoken = '120b45603b04d66d643db9a2bbfa5e20529fb608cfa52b7f6beaea554aaef0547372962f983fd6fbaeca2'
        self.core = vk_core.vk_core(vktoken)

        self.actions = []
        self.threads = []
        self.alphabet = [['s','S','с','С','$','ς','c','С','C','Ç','ᴄ','Ⓒ','匚','ᶜ','仁','⊂','☪','¢','《','[','Ĉ','{','Č','Ç','ℂ'],['০','o','O','о','О','0','ο','o','О','o','Ω','о́','ø','∅','ᴏ','Ⓞ','口','ᵒ','О','○','°','●','ø','[','Ø','ö'],['p','P','r','R','р','Р','ρ','p','Р','p','₽','ק','ř','р','尸','卩','ℙ','®','₱','ℙ'],['b','B','б','Б','β','б','Б','b','ß','b','б','6','δ','右','Ҕ','ь','Ϭ'],['e','E','е','E','ε','е','Е','e','ę','э','Э','є','Є','ᴇ','Ѣ','ъ','Ъ','Ⓔ','е́','巳','ᵉ','℮','€','£','Ē','ė','℮'],['t','T','т','Т','τ','т','Т','t','ŧ','т','7','丅','丁','Т','⚚']]
        self.chat_id = 5
        self.word = 'sorbet'
        self.word_len = len(self.word)
        self.word_prepare()

    
    def actions_add(self, action):
        self.actions.append(action)
        self.threads.append(Thread(target=action))
    
    def start(self):
        for thread in self.threads:
            thread.start()

        for thread in self.threads:
            thread.join()
    
    def pomyanem(self):
        for event in self.core.listening():        
            if event.type_id == 8 and event.chat_id == self.chat_id:
                self.core.send_message('Помянем.',chat_id=self.chat_id)
            if event.type_id == 7 and event.chat_id == self.chat_id:
                self.core.send_message('Помянем.',chat_id=self.chat_id)
                    

    def ban_new_user(self):
        newfags = []
        newfags_time = []
        newfags_state = []
        for event in self.core.listening():
            if event.type_id == 6 and event.chat_id == self.chat_id:
                newfags.append(event.info['user_id'])
                newfags_time.append(int(time.time()))
                newfags_state.append(0)
                self.core.send_message('@id' + str(event.info['user_id']) + '(' + self.core.vk_session.method('users.get',{'user_id' : event.info['user_id']})[0]['first_name'] + '), добро пожаловать в беседу каркула!\nНе забудьте отписаться, чтобы мы удостоверились, что вы не бот, и не забанили вас.',chat_id=self.chat_id)
            elif event.type == VkEventType.MESSAGE_NEW:
                if event.chat_id == self.chat_id:
                    if event.user_id in newfags:
                        ind = newfags.index(event.user_id)
                        if newfags_state[ind] == 0:
                            newfags_state[ind] = 1
                        else:
                            ind = newfags.index(event.user_id)
                            newfags.pop(ind)
                            newfags_time.pop(ind)
                            newfags_state.pop(ind)
                            self.core.send_message('Теперь вы - полноценный гражданин гвардии @smayanezikom (Карательной кулинарии), поздравляем!',chat_id=self.chat_id,forward_messages=event.message_id)
            curtime = int(time.time())
            for ind in range(len(newfags)):
                if newfags_state[ind] == 1:
                    if curtime - newfags_time[ind] > 120:
                        self.core.send_message('@id' + str(newfags[ind]) + '(' + self.core.vk_session.method('users.get',{'user_id' : newfags[ind]})[0]['first_name'] + '), вы всё ещё ничего не написали в беседе, это чревато баном.',chat_id=self.chat_id)
                        newfags_state[ind] = 2
                else:
                    if curtime - newfags_time[ind] > 300:
                        self.core.remove_user(self.chat_id, newfags[ind])
                        newfags.pop(ind)
                        newfags_time.pop(ind)
                        newfags_state.pop(ind)

    
    def jirniy(self):
        for event in self.core.events_message_chat(self.chat_id):
            if event.user_id != 379124050:
                if event.text.find('жирн') != -1 or event.text.find('Жирн') != -1:
                    time.sleep(2)
                    upload = self.core.upload.photo_messages('jir.jpg')[0]                    
                    time.sleep(1)
                    self.core.vk.messages.send(message='Кто жирный?', random_id=vk_api.utils.get_random_id(),chat_id=event.chat_id,forward_messages=event.message_id,attachment='photo' + str(upload['owner_id']) + '_' + str(upload['id']))


    def karul(self):
        while True:
            class rul_watch:
                def __init__(self, core, chat_id):
                    self.lst = []
                    self.core = core
                    self.chat_id = chat_id
                    self.stop = False

                def start(self):
                    for event in self.core.events_message_chat(self.chat_id):
                        if self.stop:
                            break
                        if event.text == 'Стреляй' or event.text == 'стреляй':
                            if event.user_id in self.lst:
                                self.core.send_message('Вы уже в игре!',chat_id=self.chat_id,forward_messages=event.message_id, delay = 2)
                            else:
                                self.lst.append(event.user_id)
                                self.core.send_message('Принято!',chat_id=self.chat_id,forward_messages=event.message_id, delay = 2)

                
                def get(self):
                    return self.lst[:]
            

            for event in self.core.events_message_chat(self.chat_id):
                if event.text == 'Карбот рулетка' or event.text == 'карбот рулетка':
                    time.sleep(2)
                    self.core.send_message('Начинаем карательную рулетку!\nЧтобы участвовать в ней, напишите "стреляй".\nУ вас есть 30 секунд для участия.',chat_id=self.chat_id,forward_messages=event.message_id, delay = 0)
                    rul_watcher = rul_watch(self.core, self.chat_id)
                    pl = Thread(target=rul_watcher.start)
                    pl.start()
                    time.sleep(10)
                    self.core.send_message('Осталось 20 секунд.',chat_id=self.chat_id, delay = 0)
                    time.sleep(10)
                    self.core.send_message('Осталось 10 секунд.',chat_id=self.chat_id, delay = 0)
                    time.sleep(5)
                    self.core.send_message('5',chat_id=self.chat_id, delay = 0)
                    time.sleep(5)
                    self.core.send_message('И победителем становится…',chat_id=self.chat_id, delay = 0)
                    players = rul_watcher.get()
                    rul_watcher.stop = True
                    if len(players) > 1:
                        uid = random.choice(players)
                        name = self.core.vk_session.method('users.get',{'user_id' : uid})[0]['first_name']

                        self.core.send_message('@id' + str(uid) + '(' + name + '), вы пидор!',chat_id=self.chat_id)
                    else:                        
                        self.core.send_message('Недостаточно игроков!',chat_id=self.chat_id)
    
    def check_suggestions(self):
        #189945062 - test
        #137996395 - kk
        group_id = 137996395
        self.core.get_news_suggested(group_id, 'wm_kk.png')
        while True:
            time.sleep(10000)
            self.core.get_news_suggested(group_id, 'wm_kk.png')

    
    def word_watcher(self):
        admin_list = [338311021,500860385,178979309,560571757,208332905,379124050]
        #banning = []
        for event in self.core.events_message_chat(self.chat_id):
            if self.word_check(event.text):
                print(event.text)
                if event.user_id != 379124050:
                    if event.user_id in admin_list:
                        if event.user_id == admin_list[0]:
                            self.core.send_message('Привет, Кеса! Хвала Священному Сорбету!',chat_id=self.chat_id,forward_messages=event.message_id)
                        else:
                            self.core.send_message('Всегда на страже сорбетопорядка!',chat_id=self.chat_id,forward_messages=event.message_id)
                    elif event.user_id == 373593096:
                        self.core.send_message('Андрюша, а тебе не бан.',chat_id=self.chat_id,forward_messages=event.message_id)
                    else:
                        self.core.send_message('Бан!',chat_id=self.chat_id,forward_messages=event.message_id)
                    '''else:
                        if event.user_id in [277183894,174005550]:
                            self.core.send_message('Благодарим за помощь в становлении сорбетной гвардии!',chat_id=self.chat_id,forward_messages=event.message_id)
                        else:
                            self.core.send_message('Бан!',chat_id=self.chat_id,forward_messages=event.message_id)'''
                    '''if event.user_id == 373593096:
                        self.core.send_message('Андрюша, с днюшей! Вкусного тебе сорбета!',chat_id=self.chat_id,forward_messages=event.message_id)
                    else:
                        self.core.send_message('Не забудь поздравить @id373593096 (Андрюшу) с прошедшим др и пожелать вкусного сорбета!',chat_id=self.chat_id,forward_messages=event.message_id)'''

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
    
    def spina_watcher(self):
        for event in self.core.events_message_chat(self.chat_id):
            if event.user_id != 379124050:
                if event.text.find('выпрямил') != -1 or event.text.find('Выпрямил') != -1:
                    self.core.send_message('Молодец! Не забывай продолжать держать спину прямой!',chat_id=self.chat_id,forward_messages=event.message_id)
                if event.text.find('Спин') != -1 or event.text.find('спин') != -1:
                    self.core.send_message('Спину нужно выпрямлять!',chat_id=self.chat_id,forward_messages=event.message_id)
    
    def ue_ban(self):
        for event in self.core.events_message_chat(self.chat_id):
            if event.user_id != 379124050:
                if event.text.find('бан') != -1 or event.text.find('Бан') != -1:
                    self.core.send_message('Уебан!',chat_id=self.chat_id,forward_messages=event.message_id)
                if event.text.find('бот') != -1 or event.text.find('Бот') != -1:
                    self.core.send_message('Уебот!',chat_id=self.chat_id,forward_messages=event.message_id)
          
bot = karbot()
bot.actions_add(bot.word_watcher)
bot.actions_add(bot.check_suggestions)
bot.actions_add(bot.karul)
bot.actions_add(bot.jirniy)
bot.actions_add(bot.ban_new_user)
bot.actions_add(bot.pomyanem)
vkthread = Thread(target=bot.start, daemon=True)
vkthread.start()

discordbot = discord.Client()

@discordbot.event
async def on_message(message):
    if message.author == discordbot.user:
        return
    #print(message.content)
    if bot.word_check(message.content):
        if message.author.id != 654998951413678126:
            await message.channel.send(f'{message.author.mention}, бан!')
        else:
            await message.channel.send('Привет, Кеса! Хвала Священному Сорбету!')

@discordbot.event
async def on_ready():
    for guild in discordbot.guilds:
        print(guild.name)
    if guild.id == 652587725236469762:
        print(
            f'{discordbot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )

discordbot.run('NjU1MDMzMjQwMzg1NDg2ODU4.XfONfA.mIhUQ1mTgzKLtJZ0yEYdJyqWyl8')
