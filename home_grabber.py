from jelly_magician.dobot.camera_dobot import CameraDobot
from jelly_magician.dobot.grabber_dobot import GrabberDobot
from jelly_magician.dobot.camera_dobot import CameraDobot
from jelly_magician.edge_impulse.classifier import Classifier

c = Classifier("some path")
cambot = CameraDobot(2, c)
cambot.move_to_standby_position()

grabot = GrabberDobot(4)
grabot.start_homing()
