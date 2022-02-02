#!/usr/bin/python

import traceback
from edge_impulse_linux.image import ImageImpulseRunner
import cv2


class Classifier:

    def __init__(self, modelfile):
        self.modelfile = modelfile

    def classify(self, img):
        if img is None:
            print("ERROR: No valid image given")
            print(traceback.format_exc())

        mf = self.modelfile
        print(mf)
        with ImageImpulseRunner(mf) as runner:
            try:
                model_info = runner.init()
                labels = model_info['model_parameters']['labels']
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                features, cropped = runner.get_features_from_image(img)
                res = runner.classify(features)

                if "classification" in res["result"].keys():
                    print('Result (%d ms.) ' % (
                        res['timing']['dsp'] + res['timing']['classification']), end='')
                    for label in labels:
                        score = res['result']['classification'][label]
                        print('%s: %.2f\t' % (label, score), end='')
                    print('', flush=True)

                elif "bounding_boxes" in res["result"].keys():
                    print('Found %d bounding boxes (%d ms.)' % (len(
                        res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                    for bb in res["result"]["bounding_boxes"]:
                        print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (
                            bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))

                return (res, cropped)

            finally:
                if (runner):
                    runner.stop()

    def draw_result(self, res, img, wait_key=False):
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
            wait_key and cv2.waitKey(0)
