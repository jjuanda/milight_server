# milight_rest
REST server for Milight/LimitlessLED/EasyBulb LED bulbs

This is a simple REST API server (Web interface to come soon) to control Milight/Limitless/EasyBulb LED lights (Check http://www.limitlessled.com/)

    $ git clone https://github.com/jjuanda/milight_server.git
    $ cd milight_server
    $ pip3 install -r requirements.txt
    $ python3 server.py
    $ # Enjoy responsibly!

TODO:
- Document commands
- Make the bridge IP configurable
- Implement all the commands available (https://github.com/yasharrashedi/LimitlessLED/blob/master/Milight.php)
