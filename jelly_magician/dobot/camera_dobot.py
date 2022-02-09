
import logging
from jelly_magician.dobot.base_dobot_controller import BaseDobotController
from jelly_magician.edge_impulse.classifier import Classifier

import cv2


class CameraDobot(BaseDobotController):
    CAMERA_POSITION = (290, 0, 30)
    MID_POSITION = (150, -150, 90)
    STANDBY_POSITION = (0, -230, 20)

    def __init__(self, device_port, classifier: Classifier):
        logger = logging.getLogger("dobot.camera_dobot")
        super().__init__(logger, device_port)
        self.classifier = classifier

    """
    +---------- DOBOT CODE ------------------------+
    """

    def move_to_camera_position(self):
        self.is_active = True
        self.move(*self.MID_POSITION, 0)
        self.move(*self.CAMERA_POSITION, 0)
        self.is_active = False

    def move_to_standby_position(self):
        self.is_active = True
        self.move(*self.MID_POSITION, 0)
        self.move(*self.STANDBY_POSITION, 0)
        self.is_active = False

    def classify(self, show_image=False):
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

    """
    +---------- CLASSIFIER CODE -------------------+
    """

    def classify(self, show_image=False):
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

    def img_debug(self):
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()
            if not ret:
                self.logger.error("Failed to grap frame")
                break
            cv2.imshow("debug", frame)
            k = cv2.waitKey(1)
            if k % 256 == 27:
                # ESC pressed
                self.logger.info("ESC hit, closing...")
                break

        cap.release()
        cv2.destroyAllWindows()
