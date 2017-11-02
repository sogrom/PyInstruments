from instruments import Meter
from base_classes import MEAS


class Metrahit(Meter):

    raw_query = "a,b,c"
    valid_modes = ['PWR', 'CAP']
    data_formats = {
        'PWR': [MEAS.REPOW, MEAS.COMPOW, MEAS.RAPOW,MEAS.POWFAC, MEAS.VOLT, MEAS.CURR, 'Mode', 'Dummy'],
        'RES': [MEAS.RES, 'Mode', 'Dummy'],
        'VDC': [MEAS.VOLT, 'Mode', 'Dummy'],
        'VAC': [MEAS.VOLT, MEAS.FREQ, 'Mode', 'Dummy'],
        'MAINS': ['Dummy'],
        'FREQ_TTL': ['Dummy'],
        'BUZ': ['Dummy'],
        'CAP': ['Dummy'],
        'IACDC': ['Dummy'],
        'IDC': ['Dummy'],
        'IAC': [MEAS.CURR, 'CF', 'Mode', 'Dummy'],
        'dB': [MEAS.CURR, 'Mode', 'Dummy']
    }
    # data_formats = {
    #     'PWR': ['RealPower', 'ComplexPower', 'ReactivePower', 'PowerFactor', 'Voltage', 'Current', 'Mode', 'Dummy'],
    #     'RES': ['Resistance', 'Mode', 'Dummy'],
    #     'VDC': ['Voltage', 'Mode', 'Dummy'],
    #     'VAC': ['Voltage', 'Frequency', 'Mode', 'Dummy'],
    #     'MAINS': ['Dummy'],
    #     'FREQ_TTL': ['Dummy'],
    #     'BUZ': ['Dummy'],
    #     'CAP': ['Dummy'],
    #     'IACDC': ['Dummy'],
    #     'IDC': ['Dummy'],
    #     'IAC': ['Current', 'CF', 'Mode', 'Dummy'],
    #     'dB': ['Magnitude', 'Mode', 'Dummy']
    #
    # }
    # REPOW= 'RealPower'
    # COMPOW='ComplexPower'
    # POWFAC='PowerFactor'
    # RAPOW='ReactivePower'


    def connected(self):
        dummy = self.port.readline()
        if dummy is not None:
            return True
        return False

    def __init__(self, ):

        system = platform.system()

        if system == "Linux":
            comport = '/dev/ttyUSB0'
        elif system == 'Windows':
            comport = 'COM11'
        print('Running on {0}, Using:{1}'.format(system, comport))
        try:
            self.port = serial.Serial(comport, 38400, timeout=0.9,
                                      parity=serial.PARITY_NONE, rtscts=0)

            dummy = self.port.readline()
            print("Opened: {0}\n\n".format(comport))
            print('Metrahit in {0} mode.'.format(self.mode))
        except serial.SerialException as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
            sys.exit(1)

    @property
    def all_data(self):
        raw_data = self.raw_query('VAL:L?').split(',')
        return dict(zip(self.data_formats[self.mode], raw_data))


    @property
    def mode(self):
        raw_mode = self.raw_query('SET?').split(',')[0]
        if raw_mode in self.data_formats.keys():
            return raw_mode
        else:
            raise ValueError('Non valid mode: {0}'.format(raw_mode))

    def raw_query(self, cmd=None):
        self.port.write('{0}\r\n'.format(cmd).encode('ascii'))
        raw = self.port.readline().decode('ascii').rstrip('\r\n').replace('1E+38','inf')
        if raw is not '':
            return raw
        else:
            raise ValueError('No data from Metrahit.')

    @property
    def data(self):
        channels = []
        dictt = self.all_data
        for k in dictt:
            if k == 'Dummy' or k == 'Mode':
                continue
            else:
                dict={
                    'MeasType': k,
                    'Value': dictt[k],
                    'Components': None,
                    'Options': dictt['Mode']
                }
                channels.append(dict)
        return channels
