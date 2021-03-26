import serial
import json


class Mate2:

    def __init__(self, device='/dev/ttyUSB0', baudrate=19200,
                 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS, timeout=2, rts=False, dtr=True,
                 readbytes=98):
        self.device = device
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.rts = rts
        self.dtr = dtr
        self.readbytes = readbytes

    def getStatus(self, format='code'):
        raw = ''
        status = {}
        try:
            raw = self._getStatusRaw()
        except Exception:
            print('mate2.getStatus exception, retry')
            raw = self._getStatusRaw()
        lines = raw.split('\r')
        print('lines={}'.format(lines))
        for line in lines:
            if len(line) < 48:
                continue
            print('line={}'.format(line))
            status[str(line[1:2])] = {
                'battery_voltage': float(line[33:36]) / 10.0,
                'charger_current': int(line[6:8]),
                'ac_input_voltage': int(line[12:15]),
                'ac_output_voltage': int(line[16:19])
            }
        if format == 'json':
            return json.dumps(status)
        return status

    def _getStatusRaw(self):
        port = serial.Serial(
            self.device,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout)
        port.setRTS(self.rts)
        port.setDTR(self.dtr)
        line = port.read(self.readbytes).decode('ascii')
        # good:
        # C,00,00,00,030,004,00,03,000,00,525,0008,00,049
        # bad:
        # C,00,04,00,03,000,00,525,0008,00,0490008,00,050
        if line[14] == ',':
            print('got bad line _getStatusRaw, retry')
            line = port.read(self.readbytes).decode('ascii')
        return line


if __name__ == '__main__':
    print(Mate2().getStatus(format='json'))
