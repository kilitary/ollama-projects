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
# method: rpropd

import concurrent.futures
import threading
import time
import math


def th(ii=0):
    idel = 0
    d = 0
    xx = 0
    sp = 0
    th_id = threading.get_native_id()
    for y in range(1, 9):
        print(f'floOr {y}')
        for x in range(random.randrange(2, 32), 55):
            x += 5 - int(y * 1.6)
            xx = x

            for a in range(3, x + int(d * 1.5)):
                a = random.randrange(1, int(a * 0.7))
                for d in range(1, a):
                    idel = int(d * 10)
                    frq = 600
                    frq += int(d * idel + x * y)
                    frq %= 5134

                    sp = random.randrange(1, 5) * 0.01

                    rnl = random.randrange(min(x, a) + 1, max(d, xx) + 100)
                    ln = (int(70 + idel + a + x +d) + rnl) % 1800
                    print(f'[{th_id:08x}] sp={sp} frq={frq} idel={idel} x={x} e={y} a={a} rnl={rnl} ln={ln}')
                    winsound.Beep(frq, ln)
                if x == xx:
                    x = random.randrange(1, int(1 + a * 5.7))
                xx = x
                if x <= 20:
                    print(f'[{th_id:08x}] uniform strip')
                    x = int(random.sample([int(x), d, y, idel, a], k=1)[0])
                if a >= 10:
                    print(f'[{th_id:08x}] uniform rip')
                    a = int(random.sample([int(x * 0.5), d, y, idel, a], k=2)[1])
                time.sleep(sp)
    return 0


th(0)

print('terminated (press enter)')

# DAINJAH
