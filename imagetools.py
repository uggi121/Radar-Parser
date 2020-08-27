import requests
import scipy.ndimage as ndimage

from io import BytesIO
from PIL import Image
from constants import *
from collections import defaultdict

def calculate_color_redness(color):
    """
    Gets the fraction of red in the RGB format of the color.
    
    Used in an older model of the program.
    """

    try:
        return color[0]/sum(color)
    except ZeroDivisionError:
        return 0

def smoothen_rgb_image(img):
    # Smoothen the given RGB image and return it. Not used in current model

    w, h = img.size
    data = img.getdata()
    smoothened_data = ndimage.gaussian_filter(data, sigma=1)
    final_data = list(map(lambda x:tuple(x), list(smoothened_data)))
    image = Image.new("RGB", (w, h))
    image.putdata(final_data)
    return image

def get_dominant_color(im, dimensions):
    """
    Given an image and a dimension box, return the most frequent color within the bounding box.
    
    Parameters:
        im (Image): The image to be processed.
        dimensions (4-tuple): The bounding box to which the image is cropped.
        
    Returns:
        The most frequently occurring color in the cropped image.
    """

    counts = defaultdict(int)
    im = im.crop(dimensions)
    width, height = im.size
    pixels = im.load()
    
    for i in range(width):
        for j in range(height):
            counts[pixels[i, j]] += 1
    
    counts[-1] = 0
    color = -1
    for col in counts:
        if counts[col] > counts[color]:
            color = col
    
    return color
    
def get_image_from_url(url):
    # Obtain an image from the given URL

    r = requests.get(url)
    img = Image.open(BytesIO(r.content))
    return img
    

def get_radar_image_from_url(url):
    # Get the radar image alone, without the scale and vertical profiles.

    img = get_image_from_url(url)
    return img.crop(radar_image_dimensions)