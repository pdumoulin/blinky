__author__ = "Paul Dumoulin"
__email__ = "paul.l.dumoulin@gmail.com"

import re
import time
import urllib2

request_body_fmt = '''<?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
     s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>{}</s:Body></s:Envelope>'''

try:
    import android
    droid = android.Android()
except ImportError:
    import sys
    droid = None

class wemo:
    OFF_STATE = '0'
    ON_STATES = ['1', '8']
    #ip = None
    ports = [49153, 49152, 49154, 49151, 49155]

    def __init__(self, switch_ip):
        self.ip = switch_ip      
   
    def toggle(self):
        status = self.status()
        if status in self.ON_STATES:
            result = self.off()
        elif status == self.OFF_STATE:
            result = self.on()
        else:
            raise Exception("UnexpectedStatusResponse")
        return result    
    
    def burst(self, seconds):
        status = self.status()
        if status == self.OFF_STATE:
            self.on()
            time.sleep(seconds)
            result = self.off()
            return result
        else:
            raise Exception("UnexpectedStatusResponse")

    def on(self):
        return self._send('Set', 'BinaryState', 1)

    def off(self):
        return self._send('Set', 'BinaryState', 0)

    def status(self):
        return self._send('Get', 'BinaryState')

    def name(self):
        return self._send('Get', 'FriendlyName')

    def signal(self):
        return self._send('Get', 'SignalStrength')
  
    def _get_header_xml(self, method, obj):
        return '"urn:Belkin:service:basicevent:1#%s"' % method + obj
   
    def _get_body_xml(self, method, obj, value=0):
        method = method + obj
        return '<u:%s xmlns:u="urn:Belkin:service:basicevent:1"><%s>%s</%s></u:%s>' % (method, obj, value, obj, method)
    
    def _send(self, method, obj, value=None):
        body_xml = self._get_body_xml(method, obj, value)
        header_xml = self._get_header_xml(method, obj)
        for port in self.ports:
            result = self._try_send(self.ip, port, body_xml, header_xml, obj) 
            if result:
                self.ports = [port]
            return result
        raise Exception("TimeoutOnAllPorts")

    def _try_send(self, ip, port, body, header, data):
        try:
            request = urllib2.Request('http://%s:%s/upnp/control/basicevent1' % (ip, port))
            request.add_header('Content-type', 'text/xml; charset="utf-8"')
            request.add_header('SOAPACTION', header)
            request.add_data(request_body_fmt.format(body)
            result = urllib2.urlopen(request, timeout=3)
            return self._extract(result.read(), data)
        except Exception as e:
            print str(e)
            return None

    def _extract(self, response, name):
        exp = '<%s>(.*?)<\/%s>' % (name, name)
        g = re.search(exp, response)
        if g:
            return g.group(1)
        return response

def get_args():
    result = {}
    params = droid.getIntent().result[u'extras'] if droid else {}
    result['ip'] = params['%argv1'] if droid else sys.argv[1]
    result['command'] = params['%argv2'] if droid else sys.argv[2]
    if result['command'] == 'burst':
        result['time'] = float(params['%argv3'] if droid else sys.argv[3])
    return result

def output(message):
    global droid
    if droid:
        droid.makeToast(message)
    else:
        print message

def main():
    args = get_args()
    switch = wemo(args['ip'])
    if args['command'] == 'on':
        output(switch.on())
    elif args['command'] == 'off':
        output(switch.off())
    elif args['command'] == 'toggle':
        output(switch.toggle())
    elif args['command'] == 'status':
        output(switch.status())
    elif args['command'] == 'name':
        output(switch.name())
    elif args['command'] == 'signal':
        output(switch.signal())
    elif args['command'] == 'burst':
        output(switch.burst(args['time']))
    
if __name__ == "__main__":
    main()
