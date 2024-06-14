# location: russia
# date: 2020-03-01
# so liar

# d at e: la ter
# secret: se c ret
# for: quiery
# type: help
# variant: 1-2-3-4

# uninstruct io ns
import winsound
# import
import random
import time
import math
import threading
# import "audo control"
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# volume control: get speakers
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


# cc: c lay Windows ex t sound.
# method: rprop

# change-s: (in future)
# + seed scan for a lay sound
# + simulated annealing
# + generalized

# 2nd rail - volume (implementation: speed)

def rail_1(a=0):
    # sp = random.randrange(1, 12) * 0.01
    # time.sleep(sp)
    vl = -20.0
    vl += int(a * 20.11)
    vl = random.randrange(1, 2 + abs(int(vl)))
    vl = -vl * 0.1
    # vl = min(-30, min(10, int(vl)))
    if vl <= -30.0:
        vl = random.sample([-30.0, -20.0, -10.0], k=3)[0]
    # print(f'\n[{th_id:08x}-02] uniform trip vl: {vl:2.1f}  a: {a:-2d} sp: {sp:2.1f}')
    volume.SetMasterVolumeLevel(vl, None)  # 10%


# 1ct rail: program

def rail_2(d=0, x=0, y=0, a=0, xx=0):
    idel = int(d * 10)
    frq_i = 600
    frq_i += int(d * idel + x * y)
    frq_i %= 5134
    frq_i = max(37, frq_i)

    rnl = random.randrange(min(x, a) + 1, min(x, a) + 1 + (max(d, xx) + 100))
    ln_i = min(260, 80 + (int(70 + idel + a + x + d) + rnl)) % 300

    return frq_i, ln_i


# rail #.... (upto: 4)

# rail runner

def rails_run(ai=0):
    idel = 0
    d = random.sample([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], k=1)[0]
    for y in range(1, 9):
        print(f'floOr {y}')

        for x in range(random.randrange(2, 32), 55):

            x += 5 - int(y * 1.6)
            xx = x

            for a in range(3, x + int(d * 1.5)):
                idel = random.sample([y, x, a, 1111, 9999, 2222, 4444, 7777, 6666], k=1)[0]
                a = random.randrange(1, int(a * 1.7))

                if x == xx:
                    x = random.randrange(1, int(1 + a * 5.7))
                xx = x

                if x <= 20:
                    px = x
                    x = int(random.sample([int(x), d, y, idel, a], k=1)[0])
                    print(f'[{th_id:08x}-00] uniform strip {px} => {x}')
                if a >= 10:
                    pa = a
                    a = int(random.sample([int(x * 0.5), d, y, idel, a], k=2)[1])
                    print(f'[{th_id:08x}-00] uniform rip {pa} => {a}')

                prev_ln = 0
                frq = 0
                ln = 0

                print(f'\nret->{idel:04} ')

                for d in range(1, a % 15):

                    frq, ln = rail_2(d)
                    if prev_ln > ln:
                        rail_1(a)
                        print(f'>', end='')
                    elif prev_ln < ln:
                        print(f'<', end='')
                    else:
                        print(f'+', end='')

                    prev_ln = ln

                    winsound.Beep(frq, ln)

                print(f'\n\r')
                print(f'[{th_id:08x}-xy] d={d} sp={sp} frq={frq} idel={idel} x={x} e={y} a={a} ln={ln}')

                rail_2(a=a, x=x, y=y, d=d, xx=xx)

    return 0


th_id = threading.get_native_id()
sp = 0

print(f'[{th_id:08x}---] running de-at-h rails')

rails_run(0)

print(f'[{th_id:08x}---] terminated (press enter)')

# DAINJAH
