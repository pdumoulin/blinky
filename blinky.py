__author__ = "Paul Dumoulin"
__email__ = "paul.l.dumoulin@gmail.com"

import re
import urllib2

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
  },
  'off' : {
    'body'   : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>0</BinaryState></u:SetBinaryState>',
    'header' : '"urn:Belkin:service:basicevent:1#SetBinaryState"'
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
  if droid is None:
    return {
      'ip'      : sys.argv[1],
      'command' : sys.argv[2]
    }
  else:
    params = droid.getIntent().result[u'extras']
    return {
      'ip'      : params['%target'],
      'command' : params['%action']
    }

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
    return result.read()
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
    if 'data' in commands[args['command']]:
      output(extract(result, commands[args['command']]['data']))
  elif args['command'] == 'toggle':
    status = send(args['ip'], 'status')
    if status.find('<BinaryState>1</BinaryState') > -1:
      send(args['ip'], 'off')
    elif status.find('<BinaryState>0</BinaryState') > -1:
      send(args['ip'], 'on')
    else:
      raise Exception("UnexpectedStatusResponse")
  else:
    raise Exception("InvalidCommand")

if __name__ == "__main__":
  main()
