import instruments
import loads

import matplotlib.pyplot as plt
import matplotlib.animation as animation




meter = instruments.Metrahit()
# load = loads.Array3721a()

print(meter.get_raw_data())

plt.style.use('dark_background')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

xar = []

def animate(i):



    x = meter.get_data()

    xar.append(int(x['current']))

    ax1.clear()
    ax1.plot(xar)


ani = animation.FuncAnimation(fig, animate, interval=300)
plt.show()