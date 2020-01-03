import vk_core

vktoken = '120b45603b04d66d643db9a2bbfa5e20529fb608cfa52b7f6beaea554aaef0547372962f983fd6fbaeca2'
core = vk_core.vk_core(vktoken)
uid = 167305511

albums = core.vk_session.method('photos.getAll',{'owner_id' : uid, 'count' : 200, 'no_service_albums' : 1})
albums_saved = core.vk_session.method('photos.get',{'owner_id' : uid, 'count' : 200, 'album_id' : 'saved'})
photos_count = albums['count'] + albums_saved['count']

data_mem = ''
data = open('data.txt', 'w+')
count = 200
offset = 0

while offset + count < albums['count']:
    print(offset)
    albums = core.vk_session.method('photos.getAll',{'owner_id' : uid, 'count' : 200, 'no_service_albums' : 1, 'offset' : offset})
    for photo in albums['items']:
        data_mem += str(photo['date']) + '\n'
    offset += count
offset -= count
if albums['count'] < offset + count:
    albums = core.vk_session.method('photos.getAll',{'owner_id' : uid, 'count' : albums['count'] - offset, 'no_service_albums' : 1, 'offset' : albums['count'] - offset})
    for photo in albums['items']:
        data_mem += str(photo['date']) + '\n'

offset = 0
while offset + count < albums_saved['count']:
    print(offset)
    albums_saved = core.vk_session.method('photos.get',{'owner_id' : uid, 'count' : 200, 'album_id' : 'saved', 'offset' : offset})
    for photo in albums_saved['items']:
        data_mem += str(photo['date']) + '\n'
    offset += count
offset -= count
if albums_saved['count'] < offset + count:
    albums_saved = core.vk_session.method('photos.get',{'owner_id' : uid, 'count' : albums_saved['count'] - offset, 'album_id' : 'saved',  'offset' : albums_saved['count'] - offset})
    for photo in albums_saved['items']:
        data_mem += str(photo['date']) + '\n'

data.write(data_mem)
data.close()
#for photo in albums['items']:
#    print(photo)