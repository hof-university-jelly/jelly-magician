#!/usr/bin/python
from jelly_magician.dobot.camera_dobot import CameraDobot
from jelly_magician.dobot.grabber_dobot import GrabberDobot
from jelly_magician.edge_impulse.classifier import Classifier
from jelly_magician.utils.coordinates import translate_img_to_grabber_coords
import glob
import cv2
import logging


DEVICE_PORT_CAMERA_BOT = 2
DEVICE_PORT_GRABBING_BOT = 4


def evaluate_instructions():
    """
    Evaluates the instructions provided by the resources folder
    """

    instruction_blue_box_model_path = "./jelly_magician/resources/eim/x86macos/bluebox_detection-mac-x86_64-v12.eim"
    instruction_pieces_model_path = "./jelly_magician/resources/eim/x86macos/lego_city_instruction-mac-x86_64-v9.eim"
    instruction_pages_path = "./jelly_magician/resources/instructions/2/*.png"
    logger = logging.getLogger("root.evaluate_instructions")

    logger.info("Evaluating instructions...")

    # instructions bluebox classification
    required_pieces = []
    instruction_pages = [cv2.imread(file)
                         for file in sorted(glob.glob(instruction_pages_path))]

    bluebox_classifier = Classifier(instruction_blue_box_model_path)
    for page in instruction_pages:
        bluebox_classifier.classify(page)
        bluebox_classifier.show_result_img(1)
        blue_box = bluebox_classifier.get_img_of_best_result_cropped()

        # instructions pieces classification
        pieces_classifier = Classifier(instruction_pieces_model_path)
        pieces_classifier.classify(blue_box)
        pieces_classifier.show_result_img(1)
        result = pieces_classifier.get_label_coord_dict()

        required_pieces.append(list(result.keys()))

    logger.info("Evaluating instructions done.")

    """
    returns array:
    [
        [piece1, piece2, ...], # page 1
        [piece3, piece4, ...], # page 2
    ]
    """
    return required_pieces


def fetch_pieces(instructions):
    """
    intructs the dobots to fetch the pieces required by the instructions
    """

    logger = logging.getLogger("root.fetch_pieces")
    modelfile = "./jelly_magician/resources/eim/x86macos/test_compressed-mac-x86_64-v1.eim"
    classifier = Classifier(modelfile)
    cambot = CameraDobot(DEVICE_PORT_CAMERA_BOT, classifier)
    grabber = GrabberDobot(DEVICE_PORT_GRABBING_BOT)

    cambot.move_to_standby_position()
    grabber.move_to_standby_position()

    logger.info("Fetching pieces...")

    for page in instructions:
        logger.info("")
        logger.info(f"Searching pieces for current page: {repr(page)}")
        for label in page:
            cambot.move_to_camera_position()
            cambot.classify()
            cambot.classifier.show_result_img()
            result = cambot.classifier.get_label_coord_dict()
            cropped_img = cambot.classifier.img_cropped
            if label in result.keys():
                logger.info(f"\tFound and fetching piece: {repr(label)}")
                target_coords = translate_img_to_grabber_coords(
                    result[label], cropped_img)
                cambot.move_to_standby_position()
                grabber.move_above_target(target_coords)
                grabber.grab()
                grabber.move_to_dropoff_position()
                grabber.drop()
            else:
                logger.warning(f"\tPiece {label} not found in target field")

        logger.info("Page complete")
    logger.info("Fetching pieces done.")


def show_field_and_classify_only():
    """
    Only moves camera in position and classifies the captured image. Used for debugging purposes.
    """

    modelfile = "./jelly_magician/resources/eim/x86macos/test_compressed-mac-x86_64-v1.eim"
    classifier = Classifier(modelfile)
    cambot = CameraDobot(DEVICE_PORT_CAMERA_BOT, classifier)
    grabber = GrabberDobot(DEVICE_PORT_GRABBING_BOT)

    grabber.move_to_standby_position()
    cambot.move_to_camera_position()
    cambot.show_cam_video()


def run():
    """
    Entry Point for the application
    """

    # setup logging
    level = logging.DEBUG
    format = '[%(levelname)s]\t[%(name)s]\t%(message)s'
    logging.basicConfig(format=format, level=level)

    instructions_evaluated = evaluate_instructions()
    fetch_pieces(instructions_evaluated)
