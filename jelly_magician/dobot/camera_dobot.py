
import logging
from jelly_magician.dobot.base_dobot_controller import BaseDobotController
from jelly_magician.edge_impulse.classifier import Classifier

import cv2


class CameraDobot(BaseDobotController):
    CAMERA_POSITION = (290, 0, 50)
    STANDBY_POSITION = (150, -150, 90)

    def __init__(self, device_port, classifier: Classifier):
        logger = logging.getLogger("dobot.camera_dobot")
        super().__init__(logger, device_port)
        self.classifier = classifier

    def move_to_camera_position(self):
        self.move(*self.CAMERA_POSITION, 0)

    def move_to_standby_position(self):
        self.move(*self.STANDBY_POSITION, 0)

    def classify_from_position(self, show_image=False):
        c = self.classifier
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            c.classify(frame)
        else:
            self.logger.error("classify: failed to capture image")

        if show_image:
            c.show_result_img(0)

        return c.get_label_coord_dict()

    def show_cam_video(self):
        cap = cv2.VideoCapture(0)

        if not (cap.isOpened()):
            self.logger.error('no camera found')

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret is True:
                self.classifier.classify(frame)
                self.classifier.show_result_img()