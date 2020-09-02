class user:
    def __init__(self, id):
        self.id = id

ulist = [user(0), user(1), user(2)]

for u in ulist:
    print(u.id)

print('a')

for u in ulist:
    u.id += 1

print('a')

for u in ulist:
    print(u.id)

print('a')

for u in ulist:
    if u.id == 1:
        ulist.remove(u)

for u in ulist:
    print(u.id)
