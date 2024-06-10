import winsound
import random

# Play Windows ext sound.
# method: rprop
for x in range(random.randrange(2, 10), 10):
    x += 10
    for a in range(1, x):
        for i in range(1, a):
            idel = int(i * 10)
            frq = 1300
            frq += int(i * idel)
            print(f'{frq} {idel} {x} {a}')
            winsound.Beep(frq, int(128 + idel + a + x))
        if x >= 16:
            print('uniform strip')
            x = int(random.uniform(2, 50))

print('yo terminated')
