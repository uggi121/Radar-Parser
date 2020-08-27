# Radar-Parser

Parses weather radar images and returns a list of places currently under heavy rainfall.

[Sample Radar Image](https://github.com/uggi121/Radar-Parser/blob/master/images/sample_image.png)

# About

This project was driven by my passion for meteorology. After years of manually analyzing radar images, I wanted a solution that would parse a radar image and return a list of locations under heavy rain. 

Currently, the project is designed to work with radar images from the doppler weather radar at Chennai, India. The core idea, explained below, is readily extensible. Being easy to adapt, I plan to work on this project to add support to radar imagery across India as well as Singapore.

# Execution

* In `constants.py`, enter a valid API key for the LocationIQ free API.
* Enter `python radar_parser.py` into the command-line when working at the root directory.

# How Does it Work

* The latest radar image is obtained by sending a GET request to the URL of the radar image.
* The image is then filtered to smoothen the image and remove noise such as mountains, which can erroneously show up as rainfall.
* The pixels in this image are scanned to determine locations of heavy rain by using a pre-computed map. The map stores mappings between pixel colors and rainfall intensities.
* Pixels determined to be under heavy rain are reverse-geocoded using a third party API. Geographic co-ordinates corresponding to the pixels are returned by the API in response to the requests.
* The geographic co-ordinates are mapped to their physical address and displayed to the user.
