import logging
import math


DEFAULT_GRABBER_BOUNDARIES = (
    (334, 81),  # top left
    (334, -81),  # top right
    (181, 81),  # bottom left
    (181, -81),  # bottom right
)


def translate_img_to_grabber_coords(img_coords, img, grabber_boundaries=DEFAULT_GRABBER_BOUNDARIES):
    logger = logging.getLogger(
        "utlis.coordinates.translate_img_to_grabber_coords")
    logger.setLevel(logging.WARNING)
    tl, tr, bl, br = grabber_boundaries

    # field dimensions in grabber format
    field_length = math.sqrt(((tl[0]-bl[0])**2)+((tl[1]-bl[1])**2))

    # The field processed by edge impulse is always a square so we only need one side length. Let's just get the average
    logger.debug(f"Field: {field_length}")

    # processed img is always a square, so lenght = height = width
    img_length = img.shape[0]
    logger.debug(f"Img: {img_length}")

    translation = field_length / img_length
    logger.debug(f"Translation: {translation}")

    # target coordinates in img format
    target_x, target_y, target_rotation = img_coords

    # x and y axis are inverted on img and grabber
    translated_target_x = target_y * translation
    translated_target_y = target_x * translation
    logger.debug(repr((translated_target_x, translated_target_y)))

    # add bottom left corner of the dobot field
    translated_target_x += br[0]
    translated_target_y += br[1]
    logger.debug(repr((translated_target_x, translated_target_y)))

    # TODO: remove z
    return (translated_target_x, translated_target_y, 90, target_rotation)
