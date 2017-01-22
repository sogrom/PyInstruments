from instruments import Meter


class OpenBryBM857(Meter):

    default_baud = 7800

    def connected(self):
        for _ in range(3):
            self.port.write(bytes([0xFF]))
            data = list(self.port.read(35))
            if len(data) == 35:
                return True
        return False

    @property
    def raw_data(self):
        for _ in range(10):
            self.port.write(bytes([0xFF]))
            data = list(self.port.read(35))
            if len(data) == 35:
                return data
        return None

    def unpack_data(self, raw_data):
        # Validate data
        if len(raw_data) != 35:
            raise ValueError('Invalid length {} != 35'.format(len(raw_data)))

        for byte in raw_data:
            # every byte must pass 0b11XXXX01 mask
            if byte & 0xC1 != 0xC1:
                raise ValueError('Byte {:02X} does not match the mask'.format(byte))

        # Stripe data
        stripped_data = [raw_data[0]]

        for (u_byte, l_byte) in zip(raw_data[1::2], raw_data[2::2]):
            new_byte = (((u_byte << 2) & 0xF0) | ((l_byte >> 2) & 0x0F))
            stripped_data.append(new_byte)

        return stripped_data

    @property
    def data(self):

        unpacked_data = self.unpack_data(self.raw_data)
        start = 4
        stop = 10

        # parse float value
        try:
            str_value = digits[unpacked_data[start]]
            if str_value[0] == '.':
                str_value = '-' + str_value[1:]
            str_value += ''.join(digits[k] for k in unpacked_data[start + 1:stop])
        except KeyError as ke:
            raise ValueError('Unknown character, 0b{0:08b} not in characters dict.'.format(ke.args[0]))

        try:
            flt_value = float(str_value)
            value = flt_value
        except ValueError:
            str_value = str_value.replace('.', '')
            str_value = str_value.strip()
            if str_value == '0L':
                value = float('inf')
            elif str_value == '-0L':
                value = float('-inf')
            else:
                raise ValueError('Cannot parse data: {}'.format(str_value))

        multiplier = 1
        for b_num, masks in multipliers_masks.items():
            for mask, mult in masks.items():
                if unpacked_data[b_num] & mask:
                    multiplier = mult

        component = ''
        for b_num, masks in components_masks.items():
            for mask, name in masks.items():
                if unpacked_data[b_num] & mask:
                    component += name

        swpos = switch_position[unpacked_data[1]]

        misc = ''
        for b_num, masks in misc_masks.items():
            for mask, name in masks.items():
                if unpacked_data[b_num] & mask:
                    misc += name + ', '

        return {
            'Value': value,
            'Multiplier': multiplier,
            'SwPosition': swpos,
            'AltFunctions': misc,
            'Component': component,

        }


digits = {
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
}

switch_position = {
    0xff: 'V',
    0x7f: 'V',
    0xbf: 'V',
    0xdf: 'Hz',
    0xef: 'V DIODE',
    0xfe: 'R',
    0xfd: 'F',
    0xfb: 'A',
    0xf7: 'A',
}


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


digits.update({(d | 0x80): '.' + v for d, v in digits.items()})




#
#
# olddata = [None]*35
# for _ in range(10000):
#     # t0 = time.time()
#     for _ in range(10):
#         port.write(bytes([0xFF]))
#         data = list(port.read(35))
#         if len(data) == 35:
#             break
#
#
#     newdata = unpack_data(data)
#     # t1 = time.time()
#
#     try:
#         p_data = parse_data(data)
#         print(p_data['Value']*p_data['Multiplier'],
#               p_data['SwPosition'],
#               p_data['Component'],
#               p_data['AltFunctions'])
#
#     except ValueError:
#         print('pass')
#         pass
#     # t2 = time.time()
#
#     # print(t2-t1)
#
#     # print(ndata)
#
#     # for nbyte in ndata:
#     #     try:
#     #         if nbyte & 0x80:
#     #             print('.', end='')
#     #         print(digits[nbyte & 0x7F], end='')
#     #     except KeyError:
#     #         print('X', end=' ')
#
#     start_byte = 0
#     stop_byte = 18
#     for bytenum in range(start_byte, stop_byte):
#         print('   |{0:02d}|    '.format(bytenum), end=' ')
#     print('')
#
#     for newbyte, oldbyte  in zip(newdata[start_byte:stop_byte], olddata[start_byte:stop_byte]):
#         bits_string = '0b{0:08b},'.format(newbyte)
#         if oldbyte != newbyte:
#             bits_string = '\033[31;m' + bits_string + '\033[0m'
#         print(bits_string, end=' ')
#         print('{0:#x}'.format(newbyte), end=' ')
#     print('\n')
#
#
#
#     # for byte in data[start:stop+1]:
#     #     print('{0:#X}'.format(byte), end=' ')
#
#     # print('\n')
#     # t3 = time.time()
#     olddata = newdata
#     # print('port:{}, strip:{}, print{}, total:{}'.format(t1-t0, t2-t1, t3-t2, t3-t0))
#     time.sleep(1)
# #
