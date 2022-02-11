# avnav-anchor-chain-counter-rpi-gpio
read the count pulses from reed relais on anchor winch via Raspberry PI's GPIO

# General

The plugin reads pulses from a read relais on the anchor winch.
Addtionally it need the Up/Down information anchor winch relais.

It is widely based on the
- seatalk remote plugin (https://github.com/wellenvogel/avnav-seatalk-remote-plugin),
- more nmea plugin      (https://github.com/kdschmidt1/avnav-more-nmea-plugin) and
- Seatalk1 to NMEA 0183 (https://github.com/MatsA/seatalk1-to-NMEA0183/blob/master/STALK_read.py).

# Parameter

- gpio_pulse: Define gpio where read relais is sensed (default is 4 => GPIO4 on pin 7)
- gpio_up: Define gpio where the up is sensed (default is 17 => GPI17 on pin 11)
- gpio_down: Define gpio where the up is sensed (default is 27 => GPI27 on pin 13)
- inverted: Define if input signal shall be inverted 0 => not inverted, 1 => Inverted (default is 1)
- pulldown: Define if using internal RPi pull up/down 0 => No, 1= Pull down, 2=Pull up (default is 2)

# Details

# Hardware needs
It is strongly commended to use optocoupler between seatalk 1 level and Raspberry Pi inputs.

An example for such an circuit is suggested here: https://pysselilivet.blogspot.com/2020/06/seatalk1-to-nmea-0183-converter-diy.html

![grafik](https://user-images.githubusercontent.com/98450191/153389077-942ecb63-cb50-4e82-a864-6e4f0f91789d.png)

First tests are made with th module BUCCK_817_4_V1.0.
![grafik](https://user-images.githubusercontent.com/98450191/153611941-e6ed298a-06d5-4a33-b4ed-b8fbda8201ec.png)

The reed relais is a brought one:
![grafik](https://user-images.githubusercontent.com/98450191/153611712-e395b9f1-18e5-4b43-8a93-baecb4d1e036.png)

All is connected via a 5-pin-socket
![grafik](https://user-images.githubusercontent.com/98450191/153611586-a4600594-4ae2-44e7-8802-de87d67da222.png)


# Software installation

To install this plugin please 
- install packages via: sudo apt-get update && sudo apt-get install pigpio python-pigpio python3-pigpio
- start pigpio deamon e.g. via sudo servive pigdiod restart
- create directory '/usr/lib/avnav/plugins/avnav-anchor-chain-counter-rpi-gpio' and 
- and copy the file plugin.py to this directory.

# Using in anvav

# TODOs
