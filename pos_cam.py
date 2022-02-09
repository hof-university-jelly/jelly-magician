from jelly_magician.dobot.camera_dobot import CameraDobot
from jelly_magician.dobot.camera_dobot import CameraDobot
from jelly_magician.edge_impulse.classifier import Classifier

c = Classifier("some path")
dobot = CameraDobot(2, c)
print(dobot.get_pose())
