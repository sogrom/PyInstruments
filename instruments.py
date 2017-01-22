import serial
import platform


class Meter:

    default_baud = 9600

    def __init__(self, comport='/dev/ttyUSB0', timeout=1):

        system = platform.system()

        print('Running on {0}, Using:{1}'.format(system, comport))
        try:
            self.port = serial.Serial(port=comport, baudrate=self.default_baud, timeout=timeout,
                                      parity=serial.PARITY_NONE, rtscts=0)
            print("Opened: {0}\n\n".format(comport))
            if not self.connected():
                raise ConnectionError('Connection error')
            print("Connected to device")
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

