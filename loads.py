import serial
import sys
import platform
import io
import csv
import time
from base_classes import MEAS

class Array3721a:
    raw_data = "a,b,c"
    # mode = None

    data = {
        'MeasVoltage': 0,
        'MeasCurrent': 0,
        'MeasPower': 0,
        'MeasResistance': 0,
        'SetCurrent': 0,
        'SetPower': 0,
        'SetVoltage': 0,
        'SetResistance': 0
    }
    flag = {'Connected': False,
            'Error' : False,
            'Mode': 0,
            'Order': 0,
            'SignalValue' : 0,
            'Order_Executed' : False,
            'Input_Enable': False}

    # ARRAY 372xSerise Electronic LoadSCPI Programin Guide p.26
    modes = ['CCL', 'CCH', 'CV', 'CPC', "CPV", 'CRL', 'CRM', 'CRH']
    commend_list = [ '*IDN',
                    'MODE', 'CURR',
                    'VOLT', 'POW',
                    'MEAS:CURR', 'MEAS:VOLT',
                    'MEAS:POW']

    def __init__(self):

        system = platform.system()

        if system == "Linux":
            comport = '/dev/ttyUSB1'
        elif system == 'Windows':
            comport = 'COM10'
        print('Running on {0}, Using:{1}'.format(system, comport))
        try:

            self.port = serial.Serial(comport, 38400, timeout=1,
                                      parity=serial.PARITY_NONE, rtscts=0)
            print("Opened: {0}\n\n".format(comport))

            self.flag['Order'] = '*IDN'
            idn = self.send_ask()
            print(idn)
            if idn == 'ARRAY,3721A,0,1.34-0.0-0.0\r\n':
                print('Connected')
                self.flag['Connected'] = True
            else:
                print('Connection Failed')
                self.flag['Connected'] = False
                input("Press Enter to continue...")
                sys.exit("Error: Connection Failed")

            self.flag['Order'] = 'MODE'
            self.flag['Mode'] = self.send_ask()
            print(self.flag['Mode'])

        except serial.SerialException as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            self.flag['Connected'] = False
            sys.exit(1)

    # pomiar prądu wejściowego
    def get_current(self):
        self.flag['Order'] = 'MEAS:CURR'
        meas_amp = self.send_ask()
        #self.port.write(b'MEAS:CURR?\r\n')
        #meas_amp = self.raw_data.decode('ascii').rstrip('')
        print(meas_amp.lstrip(''))
        self.data['MeasCurrent'] = float(meas_amp)

        return None

    # mierzy napięcie wejściowe
    def get_voltage(self):
        self.flag['Order'] = 'MEAS:VOLT'
        meas_v = self.send_ask()
        self.data['MeasVoltage'] = float(meas_v)
        return None

    def get_power(self):
        self.flag['Order'] = 'MEAS:POW'
        meas_pow = self.send_ask()
        self.data['MeasPower'] = float(meas_pow)
        return

    def update_data(self):
        self.get_current()
        self.get_voltage()
        self.get_power()
        return self.data

    # wartość podana do funkcji nastawia prąd
    def set_current(self, curr):
        self.data['SetCurrent'] = float(curr)
        self.flag['Order'] = 'CURR'
        self.flag['SignalValue'] = curr
        self.send_order()
        status = None
        self.update_data()
        return status

    def set_power(self, power_settings):
        self.data['SetCurrent'] = float(power_settings)
        self.flag['Order'] = 'POW'
        self.flag['SignalValue'] = power_settings
        self.send_order()
        status = None
        # self.update_data(self)
        return status

    def set_voltage(self, volt):
        self.data['SetCurrent'] = float(volt)
        self.flag['Order'] = 'VOLT'
        self.flag['SignalValue'] = volt
        self.send_order()
        self.data['SetVoltage'] = float(volt)
        status = None
        # self.update_data(self)
        return status

    def set_resistance(self, res):
        self.data['SetCurrent'] = float(res)
        self.flag['Order'] = 'RES'
        self.flag['SignalValue'] = res
        self.send_order()
        self.data['SetResistance'] = float(res)

        status = None

    def set_input(self, button):
        if button is 'off':
            self.flag['Order'] = 'INP'
            self.flag['SignalValue'] = "OFF"
            self.send_order()
            # self.port.write(b'INP OFF\r\n')
        elif button is 'on':
            self.flag['Order'] = 'INP'
            self.flag['SignalValue'] = "ON"
            self.send_order()
            # self.port.write(b'INP ON\r\n')
        status = None
        # self.update_data(self)
        return status

    def check_output(self):
        self.port.write(b'MEAS:VOLT?\r\n')
        Volt = self.port.readline().decode('ascii').rstrip('')
        self.port.write(b'MEAS:CURR?\r\n')
        Ampere = self.port.readline().decode('ascii').rstrip('')
        ok = 0
        print(Volt)
        print(Ampere)
        # if float(Volt) > self.data('setVolateg')-0.005 or float(Ampere) > self.data('SetCurrent')-0.003:
        if float(Volt) > 0.005 and float(Ampere) > 0.005:
            ok = 1
            print("run")
        else:
            print('notrun')
            self.set_input('off')
        return ok

    def send_order(self):

        SIGNAL = self.flag['Order'] + ' ' +str(self.flag['SignalValue']) + '\r\n'
        self.port.write(SIGNAL.encode('ascii'))
        print(SIGNAL)

        if self.send_ask() is self.flag['SignalValue']:
            print('Error: No Change')
            self.flag['Error'] = True
            self.flag['Order_Executed'] = True
            # print(self.flag)


        #print(self.commend_list)
        return None

    def send_ask(self):
        SIGNAL = self.flag['Order'] + "?" + '\r\n'
        # print(SIGNAL.encode('ascii'))
        self.port.write(SIGNAL.encode('ascii'))
        out=self.port.readline().decode('ascii').rstrip('')
        return out

