import logging
import time
from jelly_magician.dobot.base_dobot_controller import BaseDobotController


class GrabberDobot(BaseDobotController):
    STANDBY_POSITION = (0, -230, 20)
    DROPOFF_POSITION = (0, -230, 20)
    MID_POSITION = (180, -180, 90)
    GRABBING_POSITION = (230, 0, 130)

    def __init__(self, device_port):
        logger = logging.getLogger("dobot.grabber_dobot")
        super().__init__(logger, device_port)

    def grab(self):
        x, y, z, _r = self.get_pose()

        self.bot.grip(False)
        self.move(x, y, -38, _r)
        self.bot.grip(True)
        time.sleep(1)
        self.move(x, y, z, _r)

    def drop(self):
        self.bot.grip(False)
        self.bot.suck(False)

    def move_above_target(self, target):
        self.move(*self.MID_POSITION, 0)
        self.move(*target)

    def move_to_standby_position(self):
        self.move(*self.MID_POSITION, 0)
        self.move(*self.STANDBY_POSITION, 0)

    def move_to_dropoff_position(self):
        self.move(*self.MID_POSITION, 0)
        self.move(*self.DROPOFF_POSITION, 0)

    def move_to_grabbing_position(self):
        self.move(*self.MID_POSITION, 0)
        self.move(*self.GRABBING_POSITION, 0)
