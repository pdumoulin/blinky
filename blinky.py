__author__ = "Paul Dumoulin"
__email__ = "paul.l.dumoulin@gmail.com"

import re
import urllib2
import time

try:
    import android
    droid = android.Android()
except ImportError:
    import sys
    droid = None

ports = [49153, 49152, 49154]
commands = {
    'on' : {
        'body'   : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:SetBinaryState>',
        'header' : '"urn:Belkin:service:basicevent:1#SetBinaryState"',
        'data'   : 'BinaryState'
    },
    'off' : {
        'body'   : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>0</BinaryState></u:SetBinaryState>',
        'header' : '"urn:Belkin:service:basicevent:1#SetBinaryState"',
        'data'   : 'BinaryState'
    },
    'status' : {
        'body'   : '<u:GetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:GetBinaryState>',
        'header' : '"urn:Belkin:service:basicevent:1#GetBinaryState"',
        'data'   : 'BinaryState'
    },
    'name' : {
        'body'   : '<u:GetFriendlyName xmlns:u="urn:Belkin:service:basicevent:1"><FriendlyName></FriendlyName></u:GetFriendlyName>',
        'header' : '"urn:Belkin:service:basicevent:1#GetFriendlyName"',
        'data'   : 'FriendlyName'
    },
    'signal' : {
        'body'   : '<u:GetSignalStrength xmlns:u="urn:Belkin:service:basicevent:1"><GetSignalStrength>0</GetSignalStrength></u:GetSignalStrength>',
        'header' : '"urn:Belkin:service:basicevent:1#GetSignalStrength"',
        'data'   : 'SignalStrength'
    }
}

def get_args():
    result = {}
    params = droid.getIntent().result[u'extras'] if droid is not None else {}
    result['ip'] = sys.argv[1] if droid is None else params['%argv1']
    result['command'] = sys.argv[2] if droid is None else params['%argv2']
    if result['command'] == 'burst':
        result['time'] = sys.argv[3] if droid is None else params['%argv3']
        result['time'] = float(result['time'])
    return result

def output(message):
    if droid is None:
        print message
    else:
        droid.makeToast(message)

def send(ip, command):
    global ports
    for port in ports:
        result = try_send(ip, command, port) 
        if result is not None:
            ports = [port]
        return result
    raise Exception("TimeoutOnAllPorts")

def try_send(ip, command, port):
    try:
        request = urllib2.Request('http://%s:%s/upnp/control/basicevent1' % (ip, port))
        request.add_header('Content-type', 'text/xml; charset="utf-8"')
        request.add_header('SOAPACTION', commands[command]['header'])
        body = '<?xml version="1.0" encoding="utf-8"?>'
        body += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
        body += '<s:Body>%s</s:Body></s:Envelope>' % commands[command]['body']
        request.add_data(body)
        result = urllib2.urlopen(request, timeout=1)
        return extract(result.read(), commands[command]['data'])
    except Exception as e:
        return None

def extract(response, name):
    exp = '<%s>(.*?)<\/%s>' % (name, name)
    g = re.search(exp, response)
    if g:
        return g.group(1)
    return None

def main():
    args = get_args()
    if args['command'] in commands:
        result = send(args['ip'], args['command'])
        output(result)
    elif args['command'] == 'toggle':
        status = send(args['ip'], 'status')
        if status == '1':
            result = send(args['ip'], 'off')
        elif status == '0':
            result = send(args['ip'], 'on')
        else:
            raise Exception("UnexpectedStatusResponse")
        output(result)
    elif args['command'] == 'burst':
        status = send(args['ip'], 'status')
        if status == '1':
            raise Exception("SwitchAlreadyOn")
        elif status == '0':
            result = send(args['ip'], 'on')
            time.sleep(args['time'])
            result = send(args['ip'], 'off')
        else:
            raise Exception("UnexpectedStatusResponse")
    else:
        raise Exception("InvalidCommand")

if __name__ == "__main__":
    main()
