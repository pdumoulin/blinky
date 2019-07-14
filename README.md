# blinky
python for controlling Belkin brand Wemo WiFi switches

## Compatibility
* current version supports python3.5+
* for python2.x, use [tag 1.0.0](https://github.com/pdumoulin/blinky/tree/1.0.0)

## Usage Examples

### Switching
```python
Python 3.5.3 (default, Sep 27 2018, 17:25:39)
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from blinky import Wemo
sw>>> switch = Wemo('192.168.1.84')
>>> switch.status()
False
>>> switch.toggle()
>>> switch.status()
True
>>> switch.off()
False
>>> switch.status()
False
>>> switch.on()
True
>>>
```

### Naming
```python
Python 3.5.3 (default, Sep 27 2018, 17:25:39)
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from blinky import Wemo
>>> switch = Wemo('192.168.1.84')
>>> switch.identify()
'Bed Room AC'
>>> switch.rename('Bedroom AC')
'Bedroom AC'
>>> switch.identify()
'Bedroom AC'
>>>
```
