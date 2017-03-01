import serial
import platform

class MEAS:
    VOLT = 'Voltage'
    MAGN = 'Magnitude'
    DUTY = 'DutyCycle'
    CAP = 'Capacitance'
    FREQ = 'Frequency'
    CURR = 'Current'
    DIOD = 'Diode'
    RES = 'Resistance'
    CONT = 'Continuity'

    # raw stream type, for scopes
    RAW = 'RawData'

MEAS_UNITS = {
    MEAS.VOLT: 'V',
    MEAS.MAGN: 'dB',
    MEAS.DUTY: '%',
    MEAS.CAP: 'F',
    MEAS.FREQ: 'Hz',
    MEAS.CURR: 'A',
    MEAS.DIOD: 'V',
    MEAS.RES: 'R',
    MEAS.CONT: 'R',
}

MEAS_AC = 'AC'
MEAS_DC = 'DC'


class Meter(object):

    default_baud = 9600

    def __init__(self, comport='/dev/ttyUSB0', timeout=1):

        system = platform.system()

        print('Running on {0}, Using:{1}'.format(system, comport))
        try:
            self.port = serial.Serial(port=comport, baudrate=self.default_baud, timeout=timeout,
                                      parity=serial.PARITY_NONE, rtscts=0)
            print("Opened: {0}\n\n".format(comport))
            if not self.connected():
                raise ConnectionError('Connection error.')
            print("Device connected.")
        except serial.SerialException as e:
            raise IOError("I/O error({0}): {1}".format(e.errno, e.strerror))

    def connected(self):
        raise NotImplementedError

    @property
    def raw_data(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

        channels = [{
            'MeasType': None,
            'Value': None,
            'Components': None,
            'Options': None,
        }]

        return channels

