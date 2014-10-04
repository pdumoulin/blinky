__author__ = "Paul Dumoulin"
__email__ = "paul.l.dumoulin@gmail.com"

import sys
import urllib2
import socket

ports = [49153, 49152]
commands = {
  'on' : {
    'body'   : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:SetBinaryState>',
    'header' : '"urn:Belkin:service:basicevent:1#SetBinaryState"'
  },
  'off' : {
    'body'   : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>0</BinaryState></u:SetBinaryState>',
    'header' : '"urn:Belkin:service:basicevent:1#SetBinaryState"'
  },
  'status' : {
    'body'   : '<u:GetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:GetBinaryState>',
    'header' : '"urn:Belkin:service:basicevent:1#GetBinaryState"'
  }
}

def get_args():
  # TODO - detect if running on android
  # TODO - read in args from intent when running on android
  return {
    'ip'      : sys.argv[1],
    'command' : sys.argv[2]
  }

def build_body(command):
  return xml

def send(ip, command, ports):
  try:
    request = urllib2.Request('http://%s:%s/upnp/control/basicevent1' % (ip, ports[0]))
    request.add_header('Content-type', 'text/xml; charset="utf-8"')
    request.add_header('SOAPACTION', commands[command]['header'])
    body = '<?xml version="1.0" encoding="utf-8"?>'
    body += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    body += '<s:Body>%s</s:Body></s:Envelope>' % commands[command]['body']
    request.add_data(body)
    result = urllib2.urlopen(request, timeout=1)
    return result.read()
  except urllib2.URLError as e:
    if isinstance(e.reason, socket.timeout):
      if len(ports) == 1:
        raise Exception("AllPortsFailed")
      ports = ports[1:]
      send(ip, command, ports)
      return None
    raise

def main():
  args = get_args()
  if args['command'] in commands:
    send(args['ip'], args['command'], ports)
  elif args['command'] == 'toggle':
    # TODO - call status, then on/off
    pass
  else:
    raise Exception("InvalidCommand")

if __name__ == "__main__":
  main()
