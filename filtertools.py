import re

from constants import *

def filter_reflectivity(im, lower_bound, coordinates_to_filter):
    """
    Returns a list of co-ordinates where the radar reflectivity is above the input lower bound.
    
    Parameters:
        im (Image) : The radar image.
        lower_bound (int) : The minimum reflectivity to be captured. 
                            Reflectivity is proportional to rainfall rates.
    
    Returns:
         List of co-ordinates with radar output greater than the lower-bound.
    """

    pix = im.load()
    w, h = im.size
    result = [(i, j) 
            for i in range(w) 
            for j in range(h) 
            if pix[i, j] in reflectivity
            and reflectivity[pix[i, j]] > lower_bound
            and pix[i, j] != coordinates_to_filter[(i, j)]]
    return result

def load_filter(file_path):
    """
    Obtains the pixel-coordinates to be filtered out.
    
    Returns a dictionary where all pixel coordinates are mapped to a color. If the pixel in the current image
    carries the same color, then it forms a part of the background of the image. The dictionary returned helps
    filter such pixels out.
    
    Parameters:
        file_path (str) : Path of the filter reference text.
       
    Returns:
        dict: A mapping between pixels and background colors.
    """
    
    filt = {}
    with open(file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        numbers = re.findall(r"\d+", line)
        filt[(int(numbers[0]), int(numbers[1]))] = int(numbers[2])
    return filt