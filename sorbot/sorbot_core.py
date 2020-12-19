#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
from vk_api import audio
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.utils import get_random_id
import time, random, requests
from PIL import Image
import json

#from pydub import AudioSegment
import numpy as np
import math


class sorbot_core:
    def __init__(self, token):
        self._app_id = "2685278"
        self._vk_client_secret = "hHbJug59sKJie78wjrH8"
        self.vk_session = vk_api.VkApi(token=token)
        self.vk = self.vk_session.get_api()
        self.upload = vk_api.VkUpload(self.vk_session)
        ''' self.vk_session_a.auth()
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.tools = vk_api.VkTools(self.vk_session)
        self.upload = vk_api.VkUpload(self.vk_session)
        self.audio = audio.VkAudio(self.vk_session_a)'''
        self.longpoll = VkBotLongPoll(self.vk_session, group_id = 200577613)


    def send_message(self, text, chat_id = -1, user_id = 0, forward_messages = -1, attachment = [], delay = 5):
        #time.sleep(random.random() * delay)
        if chat_id != -1:
            if forward_messages != -1:
                self.vk.messages.send(chat_id=chat_id, message=text, random_id=get_random_id(), forward_messages = forward_messages)
            else:
                self.vk.messages.send(chat_id=chat_id, message=text, random_id=get_random_id())
        else:
            if forward_messages != -1:
                self.vk.messages.send(user_id=user_id, message=text, random_id=get_random_id(), forward_messages = forward_messages)
            else:
                self.vk.messages.send(user_id=user_id, message=text, random_id=get_random_id())

    def remove_user(self, chat_id, user_id):
        self.vk_session.method('messages.removeChatUser',{'chat_id' : chat_id, 'user_id' : user_id})

    def getevents(self):
        while True:
            try:
                return self.longpoll.check()
            except Exception as e:
                print('error', e)







