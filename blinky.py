
import re
import time
import requests

class Wemo:

    URL_TMPL = 'http://{ip}:{port}/upnp/control/basicevent1'
    HEADER_TMPL = '"urn:Belkin:service:basicevent:1#{method}{obj}"'
    BODY_TMPL = '''
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope
            xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">

            <s:Body>
                <u:{method}{obj} xmlns:u="urn:Belkin:service:basicevent:1">
                    <{obj}>{param}</{obj}>
                </u:{method}{obj}>
            </s:Body>

        </s:Envelope>
    '''

    def __init__(self, ip: str, timeout: int=3):
        self.ip = ip
        self.timeout = timeout
        self.ports = [49153, 49152, 49154, 49151, 49155]

    def toggle(self) -> None:
        if self.status():
            self.off()
        else:
            self.on()

    def burst(self, seconds: int) -> None:
        if not self.status():
            self.on()
            time.sleep(seconds)
            self.off()

    def on(self) -> bool:
        return self._status(self._send('Set', 'BinaryState', 1))

    def off(self) -> bool:
        return self._status(self._send('Set', 'BinaryState', 0))

    def status(self) -> bool:
        return self._status(self._send('Get', 'BinaryState'))

    def identify(self) -> str:
        return self._send('Get', 'FriendlyName')

    def rename(self, name: str) -> str:
        return self._send('Change', 'FriendlyName', name)

    def _status(self, status: str) -> bool:
        if '|' in status:
            status = status.split('|')[0]
        if status in ['1', '8']:
            return True
        if status in ['0']:
            return False
        raise Exception('UnknownStatus%s' % status)

    def _send(self, method: str, obj: str, param: str=None) -> str:
        headers = {
            'Content-type' : 'text/xml; charset="utf-8"',
            'SOAPACTION'   : Wemo.HEADER_TMPL.format(method=method, obj=obj)
        }
        body = Wemo.BODY_TMPL.format(method=method, obj=obj, param=param)
        for index, port in enumerate(self.ports):
            url = Wemo.URL_TMPL.format(ip=self.ip, port=port)
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    data=body,
                    timeout=self.timeout
                )
                if response.status_code == 200:
                    match = re.search(
                        '<{obj}>(.*?)<\/{obj}>'.format(obj=obj),
                        response.text
                    )
                    if match:
                        if index > 0:
                            self.ports.insert(0, self.ports.pop(index))
                        return match.group(1)
                    raise Exception('UnparsableResponse')
            except requests.exceptions.ConnectionError:
                pass
        raise Exception('ConnectionErrorAllPorts')
