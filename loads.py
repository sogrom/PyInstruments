import serial
import sys
import platform
import io
import csv

class Array3721a:


    def __init__(self):

        system = platform.system()

        if system == "Linux":
            comport = '/dev/ttyUSB1'
        elif system == 'Windows':
            comport = 'COM14'
        print('Running on {0}, Using:{1}'.format(system, comport))
        try:

            self.port = serial.Serial(comport, 9600, timeout=10,
                                      parity=serial.PARITY_NONE, rtscts=0)
            print("Opened: {0}\n\n".format(comport))
            self.port.write('*IDN?\r\n')
            idn = self.port.readline()
            print(idn)

        except serial.SerialException as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            sys.exit(1)

        self.raw_data = "a,b,c"
        self.mode = None
        self.data = {
            "voltage": 0,
            "current": 0,
            "power": 0,
        }

    def get_data(self):
        self.raw_data = self.port.readline()
        raw = self.raw_data.decode('ascii').split(',')


        self.mode = raw[1]
        self.data["voltage"] = raw[0]
        self.data["current"] = raw[2]
        self.data["power"] = raw[3]
        print(self.data, self.mode)
        return self.data


