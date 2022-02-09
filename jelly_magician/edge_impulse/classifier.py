#!/usr/bin/python

from edge_impulse_linux.image import ImageImpulseRunner
import cv2
import logging
import math


class Classifier:

    def __init__(self, modelfile):
        """Constructor"""

        self.modelfile = modelfile
        self.logger = logging.getLogger('edge_impulse.classifier')
        self.logger.setLevel(logging.CRITICAL)
        self.logger.debug(f"Using modelfile: {self.modelfile}")

    def classify(self, img):
        """Classify the passed image according to the eim model of the object"""

        self.current_image = img

        if self.current_image is None:
            self.logger.warn("No valid image given")
            return

        with ImageImpulseRunner(self.modelfile) as runner:
            try:
                model_info = runner.init()
                labels = model_info['model_parameters']['labels']
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                features, cropped = runner.get_features_from_image(img)
                res = runner.classify(features)

                if "bounding_boxes" in res["result"].keys():
                    self.logger.debug('Found %d bounding boxes (%d ms.)' % (len(
                        res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))

                    for bb in res["result"]["bounding_boxes"]:
                        self.logger.debug('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (
                            bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))

                self.result = res
                self.img_cropped = cropped

            finally:
                if (runner):
                    runner.stop()

    def show_result_img(self, wait_key=1):
        """Show classification results in opencv"""

        try:
            res = self.result
            img = self.img_cropped
        except:
            self.logger.debug('classification has no result or cropped img')
            return

        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        if "bounding_boxes" in res["result"].keys():
            for bb in res["result"]["bounding_boxes"]:
                x1 = bb['x']
                y1 = bb['y']
                x2 = bb['x'] + bb['width']
                y2 = bb['y'] + bb['height']
                label = bb['label']

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
                cv2.putText(img,
                            label,
                            (x1, y2 + 12),
                            cv2.FONT_HERSHEY_COMPLEX,
                            0.5, (0, 0, 255), 1)

            cv2.imshow('classification result', img)
            cv2.waitKey(wait_key)

    def get_img_of_best_result_cropped(self):
        """returns an image of the best scored found bounding box"""

        if self._result_has_bounding_boxes():
            bb_list = self.result["result"]["bounding_boxes"]
            best_score = 0
            best_box = None
            for bb in bb_list:
                score = bb["value"]
                if score > best_score:
                    best_box = bb
                    best_score = score

            if best_box is not None:
                return self._crop_img_by_bounding_box(best_box)

        return None

    def get_result_filtered_by_precision(self):
        """Returns the result of the classification filtered by precision uniquely"""

        if not self._result_has_bounding_boxes():
            return []

        bb_list = self.result["result"]["bounding_boxes"]
        filtered_bb_list = []

        # Find labels available in the current result
        available_labels = set(map(lambda bb: bb["label"], bb_list))

        for label in available_labels:
            # filter list by currently selected label
            bb_list_by_label = list(
                filter(lambda bb: bb["label"] == label, bb_list)
            )

            # search for bb with best precision
            best_score = 0
            best_box = None
            for bb in bb_list_by_label:
                score = bb["value"]
                if score > best_score:
                    best_box = bb
                    best_score = score

            # append the best scored result to our filtered list
            filtered_bb_list.append(best_box)

        return filtered_bb_list

    def get_coordinates_by_bb(self, bb):
        """Returns center coordinates of a given bounding_box"""

        x, y, w, h = [
            bb['x'],
            bb['y'],
            bb['width'],
            bb['height'],
        ]

        rot = 0
        if (w > h):
            rot = 90
        return (x + w / 2, y + h / 2, rot)

    def get_coordinates_relative_to_center_by_bb(self, coordinates_in_img):
        x, y, _r = coordinates_in_img
        img = self.img_cropped
        img_center_x = int(img.shape[0] / 2)
        img_center_y = int(img.shape[1] / 2)

        x_rel = x - img_center_x
        y_rel = y - img_center_y

        return (x_rel, y_rel, _r)

    def get_label_coord_dict(self):
        """Returns the filtered result in a dictionary format
        key: label
        value: centered coordinates

        example return: [
            'lego_alga': (22.4, 11, 0/90),
            'lego_seat': (42.4, 15.22),
        ]
        """
        bb_list = self.get_result_filtered_by_precision()
        dict = {}
        for bb in bb_list:
            coordinates_in_img = self.get_coordinates_by_bb(bb)
            coordinates_relative_to_center = self.get_coordinates_relative_to_center_by_bb(
                coordinates_in_img)
            dict[bb["label"]] = coordinates_relative_to_center

        return dict

    def _crop_img_by_bounding_box(self, bounding_box):
        """Return a cropped image of a bounding box"""

        img = self.current_image
        coords = [
            bounding_box['x'],
            bounding_box['y'],
            bounding_box['width'],
            bounding_box['height'],
        ]
        # scale image
        x, y, w, h = [math.floor(val * 6.25) for val in coords]
        # set width and height equally
        w, h = [max(w, h) for i in range(2)]

        # return cropped
        return img[y: y + h, x: x + w]

    def _result_has_bounding_boxes(self):
        """checks if a result with bounding_boxes is given"""
        if not hasattr(self, "result"):
            return False

        return "bounding_boxes" in self.result["result"].keys() and len(self.result["result"]["bounding_boxes"]) > 0
