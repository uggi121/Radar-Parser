# Define constants

chennai_radar_coordinates = (13.083911, 80.289676)          # Co-ordinates of the doppler radar site.
radar_scale_dimensions = (719, 75, 784, 425)                # Image dimensions of the radar image color scale.
radar_image_dimensions = (0, 200, 500, 700)                 # Image dimensions of the radar image output.
lat_per_km = 0.008993614533681086                           # Change in latitude per North/South movement equal to 1 km.
lon_per_km = 0.009233610341643583                           # Change in longitude per East/West movement equal to 1 km.
reflectivity_lower_bound = 45                               # Lowest reflectivity that corresponds to heavy rain.
sample_url = 'https://mausam.imd.gov.in/Radar/caz_chn.gif'       # Image URL.
fp = r"filter/filter.txt"                                          # Background filter for the image.
LOCATIONIQ_API_KEY = '3cdd1cff952a92'

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
