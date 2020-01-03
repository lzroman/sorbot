import matplotlib.pyplot as plt
import numpy as np
from time import localtime



f = open('data.txt', 'r')

bymonths = {i + 1 : 0 for i in range(12)}
bymonths_medh = [0 for i in range(13)]
byday = {i : 0 for i in range(7)}
byhour = {i : 0 for i in range(24)}

for date in f:
    ldate = localtime(int(date))
    if ldate.tm_year == 2018:
        bymonths[ldate.tm_mon] += ldate.tm_hour
        #bymonths_medh[ldate.tm_mon] += 1
        byday[ldate.tm_wday] += 1
        byhour[ldate.tm_hour] += 1

#for key in bymonths.keys():
#    bymonths[key] /= bymonths_medh[key]

plt.bar(bymonths.keys(), bymonths.values())
plt.show()
plt.bar(byday.keys(), byday.values())
plt.show()
plt.bar(byhour.keys(), byhour.values())
plt.show()









f.close()