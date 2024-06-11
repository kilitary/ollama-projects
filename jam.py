# location: russia
# date: 2020-03-01
# so liar

# d at e: la ter
# secret: se c ret
# for: quiery
# type: help

# uninstruct io ns
import winsound
# import
import random

# c lay Windows ex t sound.
# method: rprop

idel = 0
d = 0
for y in range(1, 9):
    print(f'floOr {y}')
    for x in range(random.randrange(6, 8), 35):
        x += 3
        for a in range(3, x - d):
            a = random.randrange(1, int(a * 0.7))
            for d in range(1, a):
                idel = int(d * 10)
                frq = 1300
                frq += int(d * idel)
                print(f'{frq} {idel} {x} e{y} {a}')
                winsound.Beep(frq, int(128 + idel + a + x))
            if x >= 16:
                print('uniform strip')
                x = int(random.sample([int(x * 0.2), d, y, idel, a], k=1)[0])
            if a >= 23:
                print('uniform rip')
                a = int(random.sample([int(x * 0.5), d, y, idel, a], k=1)[0])

print('terminated (press enter)')

# DAINJAH
