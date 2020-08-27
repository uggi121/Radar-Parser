import requests

from io import BytesIO
from PIL import Image

from collections import defaultdict
from constants import *
from util import *
from imagetools import *
from filtertools import *

import numpy as np
import scipy.ndimage as ndimage

import re
import json

def reverse_geocode(coordinates):
    """
    Reverse-geocodes the input coordinates and returns the output as a python dictionary.
   
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

def calculate_rainfall_locations(image_url):
    """
    Returns a list of locations under rainfall. Locations are described in the JSON format.
    
    The image at the given URL is retrieved via a GET request. The image is then filtered and reverse-geocoded to obtain the locations under rainfall.
    
    Parameters:
        image_url (string) : The url of the radar image.
    
    Returns:
         List of locations experiencing heavy rainfall.
    
    """
    image = get_radar_image_from_url(image_url)
    coordinates_to_filter = load_filter(fp)
    filtered_image = filter_reflectivity(image, 45, coordinates_to_filter)
    coordinates = [convert_pixels_to_coordinates(x[0], x[1]) for x in filtered_image]
    json_results = [reverse_geocode(x) for x in coordinates]
    
    return json_results

def main():
    json_results = calculate_rainfall_locations(sample_url)
    
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

