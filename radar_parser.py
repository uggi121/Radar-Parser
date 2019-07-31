import requests

from io import BytesIO
from PIL import Image

from collections import defaultdict

import numpy as np
import scipy.ndimage as ndimage

import re
import json

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

"""
reflectivity = {
     60.0: 0.4772727272727273,
     55.0: 0.6447368421052632,
     52.5: 0.6435643564356436,
     50.0: 0.5836065573770491,
     47.5: 0.5367847411444142,
     45.0: 0.49884526558891457,
     42.5: 0.47925311203319504,
     40.0: 0.35765379113018597,
     37.5: 0.3333333333333333,
     35.0: 0.2766295707472178,
     32.5: 0.2340823970037453,
     30.0: 0.17824074074074073,
     27.5: 0.1347708894878706,
     25.0: 0.10163934426229508,
     22.5: 0.0594059405940594,
     20.0: 0.05921052631578947
 }

redness = {
     (84, 52, 40): 0.4772727272727273,
     (98, 45, 9): 0.6447368421052632,
     (130, 60, 12): 0.6435643564356436,
     (178, 96, 31): 0.5836065573770491,
     (197, 121, 49): 0.5367847411444142,
     (216, 148, 69): 0.49884526558891457,
     (231, 168, 83): 0.47925311203319504,
     (250, 236, 213): 0.35765379113018597,
     (255, 255, 255): 0.3333333333333333,
     (174, 213, 242): 0.2766295707472178,
     (125, 181, 228): 0.2340823970037453,
     (77, 145, 210): 0.17824074074074073,
     (50, 123, 198): 0.1347708894878706,
     (31, 96, 178): 0.10163934426229508,
     (12, 60, 130): 0.0594059405940594,
     (9, 45, 98): 0.05921052631578947
 }
   """ 

chennai_radar_coordinates = (13.083911, 80.289676)
radar_scale_dimensions = (719, 75, 784, 425)
radar_image_dimensions = (0, 200, 500, 700)
lat_per_km = 0.008993614533681086
lon_per_km = 0.009233610341643583
url = 'http://imd.gov.in/section/dwr/img/caz_chn.gif'
fp = r"c:/py/radar/filter.txt"

def reverse_geocode(coordinates):
    reverse_url = "https://us1.locationiq.com/v1/reverse.php"

    data = {
        'key': '3cdd1cff952a92',
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




