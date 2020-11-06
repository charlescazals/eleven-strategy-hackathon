import base64
from datetime import datetime
import zlib
from typing import List, Union

import cv2
import numpy as np
from PIL import Image, ImageDraw


def get_typical_size(workers: List[List[int]]) -> int:
    """
    This method is used to obtain an order of magnitude,
    in pixels, of the characteristic size of a worker.
    
    Parameter
    ---------
    workers: list
        This is a list of list of 4 integers
        Each sublist represents a worker by the
        coordinates of the diagonal of its box

    Returns
    -------
    size: int
        an order of magnitude of workers' size
    """
    size = 0
    for worker in workers:
        size = max([size,
                    np.abs(worker[2]-worker[0]),
                    np.abs(worker[3]-worker[1])])
    
    return size

def draw_mask(zone: Union[dict, list], height: int, width: int) -> np.array:
    if type(zone) is list:
        return draw_mask_from_list(zone, height, width)
    elif type(zone) is dict:
        return draw_mask_from_dict(zone, height, width)

def draw_mask_from_list(zone: list, height: int, width: int) -> np.array:
    img = Image.new('L', (width, height), 0)
    ImageDraw.Draw(img).polygon([tuple(coord) for coord in zone], outline=1, fill=1)
    
    return np.array(img)

def draw_mask_from_dict(zone: dict, height: int, width: int) -> np.array:
    return base64_2_mask(zone['data'])

def base64_2_mask(s: str) -> np.array:
    """ 
    Suggested method from eleven to convert a bitmap into an array
    
    Parameter
    ---------
    s: string
        bitmap string that represents the mask
    
    Returns
    -------
    mask: np.array
        corresponding mask converted into an array
    """
    z = zlib.decompress(base64.b64decode(s))
    n = np.fromstring(z, np.uint8)
    
    return cv2.imdecode(n, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(bool) * 1

def get_date_from_picture_name(picture: str) -> datetime:
    return datetime.strptime(picture[-28:], '%Y-%m-%d-%H-%M-%S.jpg.json')