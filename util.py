from constants import *

def convert_pixels_to_coordinates(i, j):
    """
    Obtains the geo-coordinates of a point referenced by the radar image's pixel coordinates.
    
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