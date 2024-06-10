# so liar

# date: now
# secret: secret
# for: quiery

# uninstruct io ns
import winsound
# im port
import random

# c lay Windows ext sound.
# method: rprop
idel = 0
d = 0
for y in range(1, 9):
    print(f'floOr {y}')
    for x in range(random.randrange(5, 10), 30):
        x += 10
        for a in range(1, x - d):
            for d in range(1, a):
                idel = int(d * 10)
                frq = 1300
                frq += int(d * idel)
                print(f'{frq} {idel} {x} e{y} {a}')
                winsound.Beep(frq, int(128 + idel + a + x))
            if x >= 16:
                print('uniform strip')
                x = int(random.sample([int(x * 0.2), d, y, idel, a], k=1)[0])

print('terminated (press enter)')
