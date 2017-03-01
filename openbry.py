from base_classes import Meter, MEAS
import logging


logger = logging.getLogger('OpenBryLogger')
logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.NOTSET)


class BM857(Meter):

    default_baud = 7800
    raw_repeat = 10
    supported_measurements = (
        MEAS.VOLT,
        MEAS.MAGN,
        MEAS.DUTY,
        MEAS.CAP,
        MEAS.FREQ,
        MEAS.CURR,
        MEAS.DIOD,
        MEAS.RES,
        MEAS.CONT,
    )

    def connected(self):
        if self.raw_data:
                return True
        return False

    @property
    def raw_data(self):
        data = None
        for rep in range(self.raw_repeat+1):
            self.port.write(bytes([0xFF]))
            data = list(self.port.read(35))

            # Validate data

            if len(data) != 35:
                continue

            for byte in data:
                if byte & 0b11000011 != 0b11000001:
                    raise ValueError('Byte 0b{0:08b} does not match the mask 11XXXX01'.format(byte))

            # print('{0}'.format(data), end='\n\n')
            logger.debug("Raw data read repeated {0} times.".format(rep))
            return data

        raise ValueError('Repeated {0} times. Invalid data or timeout data: {1}'.format(self.raw_repeat, data))

    @staticmethod
    def unpack_data(raw_data):

        stripped_data = [raw_data[0]]

        for (u_byte, l_byte) in zip(raw_data[1::2], raw_data[2::2]):
            new_byte = (((u_byte << 2) & 0xF0) | ((l_byte >> 2) & 0x0F))
            stripped_data.append(new_byte)

        return stripped_data

    @property
    def data(self):

        unpacked_data = self.unpack_data(self.raw_data)

        # position of value in data frame
        start = 4
        stop = 10

        # parse float value
        try:
            str_value = lcd_chars[unpacked_data[start]]
            if str_value[0] == '.':
                str_value = '-' + str_value[1:]
            str_value += ''.join(lcd_chars[k] for k in unpacked_data[start + 1:stop])
        except KeyError as ke:
            raise ValueError('Unknown character, 0b{0:08b} not in characters dict.'.format(ke.args[0]))

        misc = []

        try:
            str_value = str_value.replace('- ', '-')
            flt_value = float(str_value)
            value = flt_value
        except ValueError:
            str_value = str_value.replace('.', '')
            str_value = str_value.strip()
            if str_value == '0L':
                value = float('inf')
            elif str_value == '-0L':
                value = float('-inf')
            elif str_value == '-----' or str_value == '':
                value = 0
                misc = ['RANGING']
            elif str_value == '1nErr':
                value = 0
                misc = ['INPUT ERROR']
            else:
                raise ValueError('Cannot parse data: {0}'.format(str_value))

        multiplier = 1
        for b_num, masks in multipliers_masks.items():
            for mask, mult in masks.items():
                if unpacked_data[b_num] & mask:
                    multiplier = mult

        components = []
        for b_num, masks in components_masks.items():
            for mask, name in masks.items():
                if unpacked_data[b_num] & mask:
                    components.append(name)

        for b_num, masks in misc_masks.items():
            for mask, name in masks.items():
                if unpacked_data[b_num] & mask:
                    misc.append(name)

        swpos = unpacked_data[1]

        if swpos == 0xff:    # 1. Vac
            mode = MEAS.VOLT
        elif swpos == 0x7f:  # 2. Vdc
            mode = MEAS.VOLT
        elif swpos == 0xbf:  # 3. mVdc
            mode = MEAS.VOLT
        elif swpos == 0xdf:  # 4. Hz
            mode = MEAS.FREQ
            if '%' in misc:
                mode = MEAS.DUTY
        elif swpos == 0xef:  # 5. V DIODE
            mode = MEAS.DIOD
        elif swpos == 0xfe:  # 6. RES
            mode = MEAS.RES
            if 'CONT' in misc:
                mode = MEAS.CONT
        elif swpos == 0xfd:  # 7. CAP
            mode = MEAS.CAP
        elif swpos == 0xfb:  # 8. A/mA
            mode = MEAS.CURR
        elif swpos == 0xf7:  # 9. uA
            mode = MEAS.CURR
        else:
            raise ValueError('Unable to parse switch position: swpos {0}'.format(swpos))

        if 'Hz' in misc:
            mode = MEAS.FREQ

        channels = [{
            'MeasType': mode,
            'Value': value * multiplier,
            'Components': components,
            'Options': misc,
        }]

        return channels


lcd_chars = {
    0b00000101: '1',
    0b01011011: '2',
    0b00011111: '3',
    0b00100111: '4',
    0b00111110: '5',
    0b01111110: '6',
    0b00010101: '7',
    0b01111111: '8',
    0b00111111: '9',
    0b01111101: '0',
    0b00000000: ' ',
    0b00000010: '-',
    0b01101000: 'L',
    0b01111010: 'E',
    0b01000110: 'n',
    0b01000010: 'r',
}
# add dot variant of every char in lcd_chars dict
lcd_chars.update({(d | 0x80): '.' + v for d, v in lcd_chars.items()})


multipliers_masks = {
    2: {
        0b10000000: 1e+6,
        0b01000000: 1e+3,
        0b00000100: 1e-6,
        0b00000010: 1e-3,
    },
    3: {
        0b01000000: 1e-9,
    }
}

components_masks = {
    3: {
        0b00001000: 'AC',
        0b00000100: 'DC',
    }
}

misc_masks = {
    2: {
        0b00010000: 'Hz',
    },
    3: {
        0b00000010: 'HOLD',
        0b00000001: 'AUTO',
    },
    10: {
        0b01000000: 'CONT',
    },
    15: {
        0b00001000: '%',
        0b00000010: 'MIN',
    },
    16: {
        0b10000000: 'REC',
        0b01000000: 'MAX',
        0b00010000: 'PP',
    },
    17: {
        0b10000000: 'DELTA',
    }
}
