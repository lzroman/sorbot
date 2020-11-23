import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


def main():
    """ Пример использования bots longpoll
        https://vk.com/dev/bots_longpoll
    """
    print('1')
    vk_session = vk_api.VkApi(token='7f440adeb64079a768803ec08f596deb51dcedf68e344a0b972747ecdefb39fb7cb4d293275d988550d48')
    print('2')

    longpoll = VkBotLongPoll(vk_session, '200577613')
    print('3')

    for event in longpoll.listen():
        print('startuem')

        if event.type == VkBotEventType.MESSAGE_NEW:
            print('Новое сообщение:')

            print('Для меня от: ', end='')

            print(event.obj.from_id)

            print('Текст:', event.obj.text)
            print()

        elif event.type == VkBotEventType.MESSAGE_REPLY:
            print('Новое сообщение:')

            print('От меня для: ', end='')

            print(event.obj.peer_id)

            print('Текст:', event.obj.text)
            print()

        elif event.type == VkBotEventType.MESSAGE_TYPING_STATE:
            print('Печатает ', end='')

            print(event.obj.from_id, end=' ')

            print('для ', end='')

            print(event.obj.to_id)
            print()

        elif event.type == VkBotEventType.GROUP_JOIN:
            print(event.obj.user_id, end=' ')

            print('Вступил в группу!')
            print()

        elif event.type == VkBotEventType.GROUP_LEAVE:
            print(event.obj.user_id, end=' ')

            print('Покинул группу!')
            print()

        else:
            print(event.type)
            print()


if __name__ == '__main__':
    main()