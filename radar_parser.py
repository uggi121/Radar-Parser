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
url = 'http://imd.gov.in/section/dwr/img/caz_chn.gif'       # Image URL.
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
        'key': LOCATIONIQ_API_KEY,
        'lat': str(coordinates[0]),
        'lon': str(coordinates[1]),
        'format': 'json'
    }

    response = requests.get(reverse_url, params=data)
    
    return json.loads(response.text)

def distance(i, j):
    dist = distance_from_centre(i, j)
    lon_shift = dist[0] * lon_per_km
    lat_shift = dist[1] * lat_per_km
    chn = chennai_radar_coordinates
    return (chn[0] + lat_shift, chn[1] + lon_shift)

def distance_from_centre(i, j):
    return (i - 250, 250 - j)

def load_filter(file_path):
    filt = {}
    with open(file_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        numbers = re.findall(r"\d+", line)
        filt[(int(numbers[0]), int(numbers[1]))] = int(numbers[2])
    return filt

filter_out = load_filter(fp)

def color_redness(color):
    try:
        return color[0]/sum(color)
    except ZeroDivisionError:
        return 0

def get_image_from_url(url):
    r = requests.get(url)
    img = Image.open(BytesIO(r.content))
    #img = img.convert('RGB')
    return img

def smoothen_rgb_image(img):
    w, h = img.size
    data = img.getdata()
    smoothened_data = ndimage.gaussian_filter(data, sigma=1)
    final_data = list(map(lambda x:tuple(x), list(smoothened_data)))
    image = Image.new("RGB", (w, h))
    image.putdata(final_data)
    return image

def get_radar_image_from_url(url):
    img = get_image_from_url(url)
    #img = smoothen_rgb_image(img)
    return img.crop(radar_image_dimensions)

def get_dominant_color(im, dimensions):
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
    
def filter_reflectivity(im, lower_bound):
    #threshold_redness = reflectivity[lower_bound]
    pix = im.load()
    w, h = im.size
    result = [(i, j) 
            for i in range(w) 
            for j in range(h) 
            if pix[i, j] in reflectivity
            and reflectivity[pix[i, j]] > lower_bound
            and pix[i, j] != filter_out[(i, j)]]
    return result




