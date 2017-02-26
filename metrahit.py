from instruments import Meter


class Metrahit(Meter):

    default_baud = 38400

    def connected(self):
        dummy = self.port.readline()
        if dummy is not None:
            return True
        return False

    raw_data = "a,b,c"
    mode = None
    data = {
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

    def get_raw_data(self):
        self.raw_data = self.port.readline()
        return self.raw_data
