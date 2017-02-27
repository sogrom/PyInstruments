import openbry


miernik = openbry.BM857()


import logging

logger = logging.getLogger('OpenBryLogger')
logger.setLevel(logging.DEBUG)
logger.debug("dupa")

import time

for _ in range(100000):
     print(miernik.data)
     time.sleep(0.2)

olddata = [255]*35

for _ in range(10000):

    newdata = miernik.unpack_data(miernik.raw_data)

    start_byte = 0
    stop_byte = 35
    for bytenum in range(start_byte, stop_byte):
        print('   |{0:02d}|    '.format(bytenum), end=' ')
    print('')

    for newbyte, oldbyte in zip(newdata[start_byte:stop_byte], olddata[start_byte:stop_byte]):
        bits_string = '0b{0:08b},'.format(newbyte)
        if oldbyte != newbyte:
            bits_string = '\033[31;m' + bits_string + '\033[0m'
        print(bits_string, end=' ')
        print('{0:#x}'.format(newbyte), end=' ')
    print('\n')

    olddata = newdata


#

#
