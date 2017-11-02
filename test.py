import instruments as instr
import time

meter = instr.Array3721a()

for _ in range(10000):
    print(meter.data)

# for _ in range(100000):
#     then = time.time()
#     data = meter.data
#     now = time.time()
#     print(now-then)
#     print(data)
#     time.sleep(0.1)
#
# for _ in range(10000):
#     packet_binary_diff()
#
# def packet_binary_diff(data, start=0, stop=35):
#
#     olddata = [255]*35
#     newdata = data
#
#     for bytenum in range(start, stop):
#         print('   |{0:02d}|    '.format(bytenum), end=' ')
#     print('')
#
#     for newbyte, oldbyte in zip(newdata[start:stop], olddata[start:stop]):
#         bits_string = '0b{0:08b},'.format(newbyte)
#         if oldbyte != newbyte:
#             bits_string = '\033[31;m' + bits_string + '\033[0m'
#         print(bits_string, end=' ')
#         print('{0:#x}'.format(newbyte), end=' ')
#     print('\n')
#
#     olddata = newdata
#
# #


# #
