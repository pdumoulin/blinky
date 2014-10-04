__author__ = "Paul Dumoulin"
__email__ = "paul.l.dumoulin@gmail.com"

import sys
import urllib2

def get_args():
  # TODO - detect if running on android
  # TODO - read in args from intent when running on android
  return {
    'ip'      : sys.argv[1],
    'command' : sys.argv[2]
  }

def build_xml(action):
  actions = {
    'on'     : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>1</BinaryState></u:SetBinaryState>',
    'off'    : '<u:SetBinaryState xmlns:u="urn:Belkin:service:basicevent:1"><BinaryState>0</BinaryState></u:SetBinaryState>'
  }
  xml = '<?xml version="1.0" encoding="utf-8"?>'
  xml += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
  xml += '<s:Body>%s</s:Body></s:Envelope>' % actions[action]
  return xml

def send(ip, port, command):
  try:
    request = urllib2.Request('http://%s:%s/upnp/control/basicevent1' % (ip, port))
    request.add_header('Content-type', 'text/xml; charset="utf-8"')
    request.add_header('SOAPACTION', '"urn:Belkin:service:basicevent:1#SetBinaryState"')
    request.add_data(build_xml(command))
    result = urllib2.urlopen(request, timeout=1)
    return True
  except:
    return False

def main():
  args = get_args()
  ports = [49153, 49152]
  for port in ports:
    success = send(args['ip'], port, args['command'])
    if success: break

if __name__ == "__main__":
  main()
