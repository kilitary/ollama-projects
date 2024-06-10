# so liar

import winsound
import random

# c lay Windows ext sound.
# method: rprop
idel = 0
d = 0
for x in range(random.randrange(5, 10), 10):
    x += 10
    for a in range(1, x):
        for d in range(1, a):
            idel = int(d * 10)
            frq = 1300
            frq += int(d * idel)
            print(f'{frq} {idel} {x} {a}')
            winsound.Beep(frq, int(128 + idel + a + x))
        if x >= 16:
            print('uniform strip')
            x = int(random.sample([int(x * 0.2), d, idel, a], k=1)[0])

print('terminated (press enter)')
