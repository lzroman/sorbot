#! /usr/bin/env python
# -*- coding: utf-8 -*-

import vk_api
from vk_api import audio
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import time, random, requests
from PIL import Image
import json

from bs4 import BeautifulSoup

class sorbot_core:
    def __init__(self, token):
        self._app_id = "2685278"
        self._vk_client_secret = "hHbJug59sKJie78wjrH8"
        self.vk_session = vk_api.VkApi(token=token, app_id=self._app_id, client_secret=self._vk_client_secret)
        self.vk_session_a = vk_api.VkApi('380988588015', 'fishglory')
        self.vk_session_a.auth()
        self.vk = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)
        self.tools = vk_api.VkTools(self.vk_session)
        self.upload = vk_api.VkUpload(self.vk_session)
        self.audio = audio.VkAudio(self.vk_session_a)
        self.wm_size = 0.2

    def send_message(self, text, chat_id = -1, user_id = 0, forward_messages = -1, attachment = [], delay = 5):
        time.sleep(random.random() * delay)
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
                data = self.longpoll.check()
                for event in data:
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.from_chat:
                            if event.chat_id == 6:
                                uname = str(event.user_id)
                                print(event.raw[-2])
                                if 'attach1_type' in event.raw[-2].keys():
                                    if event.raw[-2]['attach1_type'] == 'audio':
                                        mdata = event.raw[-2]['attach1'].split('_')
                                        print(mdata)
                                        wtf = self.audio.get_audio_by_id(int(mdata[0]), int(mdata[1]))
                                        print(wtf)

                return data
                return self.longpoll.check()



            except Exception as e:
                print('error', e)

    def get_news_suggested(self, public_id, path):
        wm = Image.open(path)
        wall = self.tools.get_all('wall.get', 100, {'owner_id': -public_id, 'filter': 'suggests'})
        print(wall['count'])
        for post in wall['items']:
            post['post_id'] = post['id']
            if 'attachments' in post.keys():
            #if len(post['attachments']) > 0:
                newattachments = ''
                for attachment in post['attachments']:
                    if attachment['type'] != 'photo' and 'owner_id' in attachment.keys():
                        newattachments += ',' + attachment['type'] + str(attachment[attachment['type']]['owner_id']) + '_' + str(attachment[attachment['type']]['id'])
                    else:
                        z = 0
                        y = 0
                        for size in attachment['photo']['sizes']:
                            if 'x' == size['type'] and y == 0 and z == 0:
                                getsize = size
                            if 'y' == size['type'] and z == 0:
                                y = 1
                                getsize = size
                            if 'z' == size['type']:
                                z = 1
                                getsize = size
                            if 'w' == size['type']:
                                getsize = size
                                break
                        open('tempfile.jpg', 'wb').write(requests.get(getsize['url']).content)
                        im = Image.open('tempfile.jpg')
                        width, height = im.size
                        if width > height:
                            newwidth = int(width * self.wm_size)
                            newheight = int(wm.size[1] * newwidth / wm.size[0])
                        else:
                            newheight = int(height * self.wm_size)
                            newwidth = int(wm.size[0] * newheight / wm.size[1])
                        tempwm = wm.resize((newwidth, newheight))
                        xpos = random.randrange(width - newwidth)
                        ypos = random.randrange(height - newheight)
                        im.paste(tempwm, (xpos, ypos), tempwm)
                        im.save('newtempfile.jpg')
                        upload = self.upload.photo_wall('newtempfile.jpg', group_id = public_id)
                        newattachments += ',photo' + str(upload[0]['owner_id']) + '_' + str(upload[0]['id'])
                post['attachments'] = newattachments
                if post['text'].find('#конкурс_каркул') != -1 or post['text'].find('#Конкурс_каркул') != -1:
                    poll = self.vk_session.method('polls.create',{'question' : 'Карательность блюда', 'is_anonymous' : 1, 'add_answers' : json.dumps(['1','2','3','4','5'])})
                    #print(poll)
                    newattachments += ',poll' + str(poll['owner_id']) + '_' + str(poll['id'])
                newpost = dict()
                newpost['attachments'] = newattachments[1:]
                newpost['owner_id'] = -public_id
                newpost['message'] = post['text']
                newpost['post_id'] = post['id']
                newpost['publish_date'] = int(time.time() + 2000000)
                newpost['signed'] = 1
                self.vk_session.method('wall.post', newpost)








