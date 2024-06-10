import winsound

# Play Windows ext sound.
# method: rprop
for x in range(1, 50):
    x += 10
    for a in range(1, x):
        for i in range(1, a):
            idel = i * 10
            frq = 1300
            frq += i * idel
            print(frq)
            winsound.Beep(frq, 128 + idel + a + x)

print('terminated')
