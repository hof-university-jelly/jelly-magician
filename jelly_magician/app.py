#!/usr/bin/python
from re import A
from jelly_magician.dobot.base_dobot_controller import BaseDobotController
from jelly_magician.dobot.camera_dobot import CameraDobot
from jelly_magician.dobot.grabber_dobot import GrabberDobot
from jelly_magician.edge_impulse.classifier import Classifier
import glob
import cv2
import logging

DEVICE_PORT_CAMERA_BOT = 2
DEVICE_PORT_GRABBING_NOT = 4


def evaluate_instructions():
    instruction_blue_box_model_path = "./jelly_magician/resources/eim/x86macos/bluebox_detection-mac-x86_64-v12.eim"
    instruction_pieces_model_path = "./jelly_magician/resources/eim/x86macos/lego_city_instruction-mac-x86_64-v9.eim"
    instruction_pages_path = "./jelly_magician/resources/instructions/2/*.png"

    """
    instructions bluebox classification
    """
    required_pieces = []
    instruction_pages = [cv2.imread(file)
                         for file in sorted(glob.glob(instruction_pages_path))]

    bluebox_classifier = Classifier(instruction_blue_box_model_path)
    for page in instruction_pages:
        bluebox_classifier.classify(page)
        bluebox_classifier.show_result_img(1)
        blue_box = bluebox_classifier.get_img_of_best_result_cropped()

        """
        instructions pieces classification
        """
        pieces_classifier = Classifier(instruction_pieces_model_path)
        pieces_classifier.classify(blue_box)
        pieces_classifier.show_result_img(1)
        result = pieces_classifier.get_label_coord_dict()

        required_pieces.append(list(result.keys()))

    # arr[page][piece1, piece2, ...]
    return required_pieces


def show_cam_video(dobot=None):
    cap = cv2.VideoCapture(0)

    if not (cap.isOpened()):
        logging.error('no camera found')

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret is True:
            classify_video_frame(frame)
            if dobot is not None:
                logging.debug(dobot.bot.pose())


def classify_video_frame(frame):
    real_pieces_model_path = "./jelly_magician/resources/eim/x86macos/test_compressed-mac-x86_64-v1.eim"
    c = Classifier(real_pieces_model_path)
    c.classify(frame)
    c.show_result_img()


def use_instructions(pieces_per_page):
    real_pieces_model_path = "./jelly_magician/resources/eim/x86macos/test_compressed-mac-x86_64-v1.eim"

    for pieces in pieces_per_page:

        cap = cv2.VideoCapture(0)
        # dobot = DobotController(port=2)
        dobot = BaseDobotController(port=4)
        dobot.move(*dobot.DEFAULT_POS, 0)
        c = Classifier(real_pieces_model_path)

        if not (cap.isOpened()):
            logging.error('no camera')

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret is True:
                for piece in pieces:
                    logging.debug(f"Looking for Piece: {piece}")
                    if dobot.ready:
                        c.classify(frame)
                        c.show_result_img()
                        classification_result = c.get_label_coord_dict()
                        if piece in classification_result.keys():
                            target_coords = classification_result[piece]
                            dobot.grab_object(target_coords, c.current_image)
                    else:
                        continue


def pose(dobot):
    logging.debug(dobot.get_pose())
    exit(0)


def foo():
    modelfile = "./jelly_magician/resources/eim/x86macos/test_compressed-mac-x86_64-v1.eim"
    classifier = Classifier(modelfile)
    cambot = CameraDobot(DEVICE_PORT_CAMERA_BOT, classifier)
    grabber = GrabberDobot(DEVICE_PORT_GRABBING_NOT)

    grabber.move_to_standby_position()
    cambot.move_to_camera_position()
    cambot.img_debug()


def run():
    # setup logging
    level = logging.DEBUG
    format = '[%(levelname)s]\t[%(name)s]\t%(message)s'
    logging.basicConfig(format=format, level=level)

    foo()
