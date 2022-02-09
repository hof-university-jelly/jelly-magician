from logging import Logger
from threading import Thread
from serial.tools import list_ports

from jelly_magician.dobot.jelly_dobot import JellyDobot
from jelly_magician.edge_impulse.classifier import Classifier


class BaseDobotController:

    def __init__(self, logger: Logger, port=2):
        self.logger = logger
        self.bot = self.init_bot(port)
        self.is_active = False

    def init_bot(self, port):
        ports = list_ports.comports()
        # self.logger.debug("ports: {}".format(ports))

        if (len(ports) == 0):
            self.logger.error("No Dobot detected")
            return None

        device_port = ports[port].device
        device = JellyDobot(port=device_port, verbose=False)

        return device

    def get_pose(self):
        pose = self.bot.pose()
        return (pose[0], pose[1], pose[2], pose[3])

    def start_homing(self):
        self.bot._start_homing(True)

    def await_pos(self, bot, x, y, z, r, homing=False):
        tresh = 5
        count = 0
        fin = False
        if not homing:
            bot.move_to(x, y, z, r)
        while count < 15:
            try:
                bx, by, bz, br = self.get_pose()
                if ((x-tresh) < bx and bx < (x+tresh)):
                    if ((y-tresh) < by and by < (y+tresh)):
                        if ((z-tresh) < bz and bz < (z+tresh)):
                            fin = True
                            break
            except:
                pass
            count += 1
        if not fin:
            self.logger.critical("Arm could not reach position!")

    def move(self, x, y, z, r, homing=False):
        self.is_active = True
        thread = Thread(target=self.await_pos, args=(
            self.bot, x, y, z, r, homing))
        thread.start()
        thread.join()
        self.is_active = False

    def is_active(self):
        return self.is_active
