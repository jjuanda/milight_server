import sys
import socket
from datetime import datetime


UDP_IP = "255.255.255.255" #this is the IP of the wifi bridge, or 255.255.255.255 for UDP broadcast
UDP_IP = "192.168.1.2" #this is the IP of the wifi bridge, or 255.255.255.255 for UDP broadcast
UDP_PORT = 8899


print ("UDP target IP:", UDP_IP) #don't really need this
print ("UDP target port:", UDP_PORT) #don't really need this



class Milight:
    def __init__(self, ip = "192.168.1.2", port = 8899):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mode = None
        self.color = None
        self.brightness = None
        self.cmddelay = .1
        self.frac_secs = 8
        self.frac_step = 1./self.frac_secs

    def send(self, msg):
        self.sock.sendto(msg, (self.ip, self.port))

    def off(self):
        self.send(bytes([65, 0, 85]))

    def on(self):
        self.send(bytes([66, 0, 85]))

    def setbrightness(self, brightness):
        self.send(bytes([66, 0, 85]))
        self.brightness = brightness
        self.send(bytes([78, brightness, 85]))

    def setcolor(self, color):
        self.send(bytes([66, 0, 85]))
        self.color = color
        self.mode = "rgb"
        self.send(bytes([64, color, 85]))

    def colorbrightness(self, color, brightness):
        self.setcolor(color)
        time.sleep(self.cmddelay)
        self.setbrightness(brightness)

    def setwhite(self):
        self.send(bytes([66, 0, 85]))
        self.send(bytes([194, 0, 85]))
        self.mode = "white"

    def whitebrightness(self, brightness):
        self.setwhite()
        time.sleep(self.cmddelay)
        self.setbrightness(brightness)

    def nightmode(self):
        self.send(b'\x41\x00\xC1')

    def colortransition(self, to, transitiontime):
        from_color = self.color
        from_brightness = self.brightness
        to_color, to_brightness = to

        frac_secs = 4

        num_steps = transitiontime*frac_secs # Each 250ms

        r_color = (to_color - from_color)/float(num_steps)
        r_brightness = (to_brightness - from_brightness)/float(num_steps)

        for i in range(0, num_steps):
            new_color = int(from_color + r_color*i)
            new_brightness = int(from_brightness + r_brightness*i)
            if new_color != self.color or new_brightness != self.brightness:
                self.colorbrightness(new_color, new_brightness)

            time.sleep(self.frac_step)

    def whitetransition(self, to_brightness, transitiontime):
        from_brightness = self.brightness

        num_steps = transitiontime*self.frac_secs # Each 250ms

        r_brightness = (to_brightness - from_brightness)/float(num_steps)

        for i in range(0, num_steps):
            new_brightness = int(from_brightness + r_brightness*i)
            if new_brightness != self.brightness:
                self.whitebrightness(new_brightness)

            time.sleep(self.frac_step)


class CommandSequencer:
    def __init__(self, execcls):
        self.execcls = execcls

    def log_message(self, msg):
        print ("[%s] %s" % (datetime.now().strftime("%H:%M"), msg))

    def run(self, lcmds):
        for l in lcmds:
            cmd = l['command']
            if cmd == "pause":
                self.log_message ("Pausing for %s seconds" % l['time'])
                time.sleep(l['time'])
            elif cmd == "setwhite":
                self.log_message ("White")
                self.execcls.setwhite()
            elif cmd == "setcolor":
                self.log_message ("Setting color to %s" % l['value'])
                self.execcls.setcolor(l['value'])
            elif cmd == "setbrightness":
                self.log_message ("Setting brightness to %s" % l['value'])
                self.execcls.setbrightness(l['value'])
            elif cmd == "off":
                self.log_message ("Off")
                self.execcls.off()
            elif cmd == "on":
                self.log_message ("On")
                self.execcls.on()
            elif cmd == "colortransition":
                self.log_message ("Color transition to %s in %s seconds" % ((l['color'], l['brightness']), l['time']))
                self.execcls.colortransition((l['color'], l['brightness']), l['time'])
            elif cmd == "whitetransition":
                self.log_message ("White transition to %s in %s seconds" % (l['value'], l['time']))
                self.execcls.whitetransition(l['value'], l['time'])
            else:
                self.log_message ("Unsupported command: %s" % l)

            time.sleep(.15)
