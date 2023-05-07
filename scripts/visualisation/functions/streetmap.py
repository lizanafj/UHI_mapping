# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 08:54:33 2021

@author: elisa+Jesus Lizana


"""

from urllib.request import urlopen, Request
import io
from PIL import Image

##############################################################################
#PLOTEO DE PUNTOS SOBRE MAPA USANDO CARTOPY - street map API
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
##############################################################################

def image_spoof(self, tile): # this function pretends not to be a Python script
    url = self._image_url(tile) # get the url of the street map API
    req = Request(url) # start request
    req.add_header('User-agent','Anaconda 3') # add user agent to request
    fh = urlopen(req) 
    im_data = io.BytesIO(fh.read()) # get image
    fh.close() # close url
    img = Image.open(im_data) # open image with PIL
    img = img.convert(self.desired_tile_form) # set image format
    return img, self.tileextent(tile), 'lower' # reformat for cartopy









