#!/usr/bin/python
from jelly_magician.edge_impulse.classifier import Classifier
import glob
import cv2
import logging


def show_cam_video():
    cap = cv2.VideoCapture(1)

    if not (cap.isOpened()):
        logging.error('no camera')

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret is True:
            classify_video_frame(frame)


def classify_video_frame(frame):
    real_pieces_model_path = "./jelly_magician/resources/eim/x86macos/test_compressed-mac-x86_64-v1.eim"
    c = Classifier(real_pieces_model_path)
    c.classify(frame)
    c.show_result_img()


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
        bluebox_classifier.show_result_img(0)
        blue_box = bluebox_classifier.get_img_of_best_result_cropped()

        """
        instructions pieces classification
        """
        pieces_classifier = Classifier(instruction_pieces_model_path)
        pieces_classifier.classify(blue_box)
        pieces_classifier.show_result_img(0)
        result = pieces_classifier.get_label_coord_dict()

        required_pieces.append(list(result.keys()))

    # arr[page][piece1, piece2, ...]
    return required_pieces


def run():
    # setup logging
    level = logging.DEBUG
    format = '[%(levelname)s]\t[%(name)s]\t%(message)s'
    logging.basicConfig(format=format, level=level)

    # run app
    pieces_needed = evaluate_instructions()
