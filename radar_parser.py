import requests

from io import BytesIO
from PIL import Image

from collections import defaultdict

import numpy as np
import scipy.ndimage as ndimage

import re
import json

# Define rainfall intensities corresponding to image color codes.
reflectivity = {
     73: 60.0,
     109: 57.5,
     108: 55.0,
     144: 52.5,
     186: 50.0,
     192: 47.5,
     204: 45.0,
     210: 42.5,
     214: 40.0,
     215: 37.5,
     143: 35.0,
     101: 32.5,
     23: 30.0,
     17: 27.5,
     11: 25.0,
     4: 22.5,
     3: 20.0
     }

# Define constants

chennai_radar_coordinates = (13.083911, 80.289676)          # Co-ordinates of the doppler radar site.
radar_scale_dimensions = (719, 75, 784, 425)                # Image dimensions of the radar image color scale.
radar_image_dimensions = (0, 200, 500, 700)                 # Image dimensions of the radar image output.
lat_per_km = 0.008993614533681086                           # Change in latitude per North/South movement equal to 1 km.
lon_per_km = 0.009233610341643583                           # Change in longitude per East/West movement equal to 1 km.
sample_url = 'https://mausam.imd.gov.in/Radar/caz_chn.gif'       # Image URL.
fp = r"filter.txt"                                          # Background filter for the image.

def reverse_geocode(coordinates):
    """
    Reverse-geocode the input coordinates and return the output as a python dictionary.
   
    Uses LocationIQ's reverse-geocoding service. Their API was chosen due to an upper bound
    of 10,000 free API calls a day.
    
    Parameters:
         coordinates (tuple) : A pair of the form (latitude, longitude)
        
    Returns:
         dict: A dictionary obtained from the JSON response.
    """
     
    reverse_url = "https://us1.locationiq.com/v1/reverse.php"

    data = {
        'key': '3cdd1cff952a92',
        'lat': str(coordinates[0]),
        'lon': str(coordinates[1]),
        'format': 'json'
    }

    response = requests.get(reverse_url, params=data)
    
    return json.loads(response.text)

def convert_pixels_to_coordinates(i, j):
    """
    Obtain the geo-coordinates of a point referenced by the radar image's pixel coordinates.
    
    Parameters:
         i (int) : x-coordinate of the pixel.
         j (int) : y-coordinate of the pixel.
          
    Returns:
         tuple: A pair of coordinates of the form (latitude, longitude).
    """
     
    dist = calculate_distance_from_centre(i, j)
    lon_shift = dist[0] * lon_per_km
    lat_shift = dist[1] * lat_per_km
    chn = chennai_radar_coordinates
    return (chn[0] + lat_shift, chn[1] + lon_shift)

def calculate_distance_from_centre(i, j):
    # Obtain the pixel coordinates of a point relative to the centre, i.e (250, 250)

    return (i - 250, 250 - j)

def load_filter(file_path):
    """
    Obtain the pixel-coordinates to be filtered out.
    
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

def calculate_color_redness(color):
    """
    Get the fraction of red in the RGB format of the color.
    
    Used in an older model of the program.
    """

    try:
        return color[0]/sum(color)
    except ZeroDivisionError:
        return 0

def get_image_from_url(url):
    # Obtain an image from the given URL

    r = requests.get(url)
    img = Image.open(BytesIO(r.content))
    #img = img.convert('RGB')
    return img

def smoothen_rgb_image(img):
    # Smoothen the given RGB image and return it. Not used in current model

    w, h = img.size
    data = img.getdata()
    smoothened_data = ndimage.gaussian_filter(data, sigma=1)
    final_data = list(map(lambda x:tuple(x), list(smoothened_data)))
    image = Image.new("RGB", (w, h))
    image.putdata(final_data)
    return image

def get_radar_image_from_url(url):
    # Get the radar image alone, without the scale and vertical profiles.

    img = get_image_from_url(url)
    #img = smoothen_rgb_image(img)
    return img.crop(radar_image_dimensions)

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
    
    #print(counts)
    counts[-1] = 0
    color = -1
    for col in counts:
        if counts[col] > counts[color]:
            color = col
    
    return color
    
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

    #threshold_redness = reflectivity[lower_bound]
    pix = im.load()
    w, h = im.size
    result = [(i, j) 
            for i in range(w) 
            for j in range(h) 
            if pix[i, j] in reflectivity
            and reflectivity[pix[i, j]] > lower_bound
            and pix[i, j] != coordinates_to_filter[(i, j)]]
    return result

def main():
    image = get_radar_image_from_url(sample_url)
    coordinates_to_filter = load_filter(fp)
    filtered_image = filter_reflectivity(image, 45, coordinates_to_filter)
    coordinates = [convert_pixels_to_coordinates(x[0], x[1]) for x in filtered_image]
    json_results = [reverse_geocode(x) for x in coordinates]
    #print(json_results)
    
    final_results = []
    
    for result in json_results:
        try:
            final_results.append(result['display_name'])
        except KeyError:
            pass
    
    places = set(final_results)
    for place in places:
        print(place)

if __name__ == "__main__":
    main()

