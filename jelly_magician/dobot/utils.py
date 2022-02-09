"""
TODO: BROKE AS FUCK
"""


def scan_for(self, label):
    for section in self.SCAN_SECTIONS:
        self.move(*section, 0)
        self.classify_from_position()
        self.classifier.show_result_img(1)
        result = self.classifier.get_label_coord_dict()
        self.logger.debug(repr(result))

        if label in result.keys():

            # self.grab_object(result[label], self.classifier.current_image)
            self.logger.info(f"Found Piece: {label}")
            target_coords = self.translate_img_to_bot_coords(result[label])
            # self.move_above_cam()

            self.move(*target_coords)
            self.grab(0)
            # self.classify_from_position()
            # res_ = self.classifier.get_label_coord_dict()
            # self.logger.debug(repr(res_))
            # self.classifier.show_result_img(0)
            break


def translate_img_to_bot_coords(self, img_coords):
    """
    Translate target coordinates on the image into coordinates which the dobot arm can target
    """
    img_x, img_y, img_r = img_coords
    self.logger.debug(f"img_coords: {repr(img_coords)}")

    # Since the image is taken on z:130 we need to scale the coordinates down
    scale = self.BOT_STEP_SCALE
    scale = 0.65
    img_x_scaled = img_x * scale
    img_y_scaled = img_y * scale
    self.logger.debug(
        f"img_coords scaled: {repr((img_x_scaled, img_y_scaled))}")

    # Current bot coordinates
    bot_x, bot_y, _bot_y, _bot_r = self.get_pose()
    self.logger.debug(f"bot_coords: {repr((bot_x, bot_y))}")

    # Target coordinates are current bot coordinates + scaled img coordinates + camera position offset
    cam_offset_x = self.CAM_OFFSET_X
    cam_offset_y = self.CAM_OFFSET_Y

    # apply camera offset
    target_x = bot_x
    target_y = bot_y
    target_x = bot_x + cam_offset_x  # TODO
    target_y = bot_y + cam_offset_y

    self.logger.debug(f"target_coords: {repr((target_x, target_y))}")

    # apply scaled img offset.
    target_x = target_x - img_y_scaled
    target_y = target_y - img_x_scaled

    self.logger.debug(
        f"target_coords w image: {repr((target_x, target_y))}")

    return (target_x, target_y, 50, 0)
