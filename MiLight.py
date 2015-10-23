import time
import sys
import socket
from datetime import datetime
import re
import struct
import colorsys


UDP_IP = "255.255.255.255" #this is the IP of the wifi bridge, or 255.255.255.255 for UDP broadcast
UDP_IP = "192.168.1.2" #this is the IP of the wifi bridge, or 255.255.255.255 for UDP broadcast
UDP_PORT = 8899


print ("UDP target IP:", UDP_IP) #don't really need this
print ("UDP target port:", UDP_PORT) #don't really need this



class Milight:
    def __init__(self, ip = "192.168.1.2", port = 8899):
        self.ip         = ip
        self.port       = port
        self.sock       = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.mode       = None
        self.color      = None
        self.brightness = None
        self.cmddelay   = .1
        self.frac_secs  = 8
        self.frac_step  = 1./self.frac_secs

    def set_ip(self, ip):
        aa = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)
        if aa:
            print("Setting Bridge IP to %s" % ip)
            self.ip = ip
        else:
            raise ValueError("Invalid IP address: %s" % ip)

    def send(self, msg):
        self.sock.sendto(msg, (self.ip, self.port))

    def off(self):
        self._send_commands(([65, 0], ))

    def on(self):
        self._send_commands(([66, 0], ))

    def group_on(self, group):
        cmd = 69 + (int(group) - 1) * 2
        self._send_commands(([cmd, 0], ))

    def group_off(self, group):
        cmd = 70 + (int(group) - 1) * 2
        self._send_commands(([cmd, 0], ))

    def set_brightness(self, brightness):
        if brightness == 0:
            self.brightness = 0
            self.off()
        else:
            if self.brightness == 0:
                self.on()
            self._send_commands(([66, 0], [78, brightness]))
            self.brightness = brightness

    def _hex_to_rgb_color(self, hex_color):
        res = struct.unpack('BBB', hex_color)
        print("hex > int: %s > %s" % (hex_color, res))
        return res

    def _rgb_to_milight_color(self, rgb):
        return int(255.*(1.-colorsys.rgb_to_hls(rgb[0], rgb[1], rgb[2])[0]) + 192) % 255

    def _hex_to_milight_color(self, hex_color):
        return self._rgb_to_milight_color (self._hex_to_rgb_color(hex_color))

    def _send_commands(self, cmds):
        for cmd in cmds:
            self.send(bytes([cmd[0], cmd[1], 85]))
            time.sleep(self.cmddelay)

    def set_hex_color(self, hex_color):
        color = self._hex_to_milight_color(bytearray.fromhex(hex_color))
        self.set_color(color)

    def set_color(self, hue):
        self.on()

        # hue = int(((270 - int(hue)) % 360) * 255 / 360)
        hue = (256 + 176 - int(int(hue) / 360.0 * 255.0)) % 256
        print("hue: %s" % hue)
        self.color = hue
        self.mode  = "rgb"
        self._send_commands(([64, hue], ))

    def colorbrightness(self, color, brightness):
        self.set_color(color)
        time.sleep(self.cmddelay)
        self.brightness(brightness)

    def nightmode(self):
        self._send_commands(([65, 0], [193, 0]))
        self.mode = "nightmode"

    def discomode(self):
        self._send_commands(([77, 0], ))
        self.mode = "discomode"

    def set_white(self):
        self._send_commands(([66, 0], [194, 0]))
        self.mode = "white"

    def whitebrightness(self, brightness):
        self.set_white()
        self.set_brightness(brightness)

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

        from_brightness = self.brightness if self.brightness is not None else 2
        to_brightness = int(to_brightness)
        print("White transition from %s to %s in %s secs" % (from_brightness, to_brightness, transitiontime))

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
