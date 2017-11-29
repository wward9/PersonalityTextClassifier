# -*- coding: utf-8 -*-
"""
@Author: David
"""
import numpy as np
import math
import urllib
import cv2

class images:
    """Base class for loading a picture in to openCV and extracting some simple features.  Handle the possible URLError upon instantiation"""
    
    BGR = 0
    HSV = 1
    GREYSCALE = 2
    BLUE = 3
    GREEN = 4
    RED = 5
    HUE = 6
    SATURATION = 7
    VALUE = 8
    
    
    def __init__(self, url):
        resp = urllib.request.urlopen(url)
        img = np.asarray(bytearray(resp.read()), dtype = "uint8")
        self.dicts = [{} for x in range(9)]
        self.dicts[self.BGR]['image'] = cv2.imdecode(img, cv2.IMREAD_COLOR)
        
    def get_img(self, variant):
        """Returns images for BGR, HSV or GREYSCALE"""
        if variant < 3:
            try:
                self.dicts[variant]['image']
            except KeyError:
                if variant == self.HSV:
                    self.dicts[variant]['image'] = cv2.cvtColor(self.dicts[self.BGR]['image'], cv2.COLOR_BGR2HSV)
                elif variant == self.GREYSCALE:
                    self.dicts[variant]['image'] = cv2.cvtColor(self.dicts[self.BGR]['image'], cv2.COLOR_BGR2GRAY)
            return self.dicts[variant]['image']
    
    def get_histogram(self, variant):
        """Returns histogram for GREYSCALE, BLUE, GREEN, RED, HUE, SATURATION, or VALUE"""
        if variant > 2 and variant < 9:
            try:
                self.dicts[variant]['histogram']
            except KeyError:
                if variant == self.GREYSCALE:
                    self.dicts[variant]['histogram'] = (np.array(cv2.calcHist(self.get_img(variant), [0], None, [256], [0,256])))
                elif variant == self.HUE:
                    self.dicts[variant]['histogram'] = (np.array(cv2.calcHist(self.get_img(variant//6), [variant%3], None, [256], [0,256])))
                else:
                    self.dicts[variant]['histogram'] = (np.array(cv2.calcHist(self.get_img(variant//6), [variant%3], None, [256], [0,256])))
            return self.dicts[variant]['histogram']
        
    def get_HS_histogram(self):
        """Returns 2D histogram for HUE/SATURATION"""
        try:
            self.dicts[self.HSV]['HS_histogram']
        except KeyError:
            self.dicts[self.HSV]['HS_histogram'] = (np.array(cv2.calcHist([self.get_img(self.HSV)], [0,1], None, [360,256], [0,360,0,256])))
        return self.dicts[self.HSV]['HS_histogram']
    
    def get_histogram_avg(self, variant):
        """Returns the average value from a histogram for GREYSCALE, BLUE, GREEN, RED, HUE, SATURATION, or VALUE"""
        try:
            self.dicts[variant]['histogram_avg']
        except KeyError:
            if variant == self.HUE:
                self.calc_hue_avg_vect()
            elif variant > self.HSV:
                self.dicts[variant]['histogram_avg'] = self.hist_avg(self.get_histogram(variant))
        return self.dicts[variant]['histogram_avg']
    
    def get_histogram_std_dvn(self, variant):
        """Returns the standard deviation for histogram for GREYSCALE, BLUE, GREEN, RED, HUE, SATURATION, or VALUE"""
        try:
            self.dicts[variant]['histogram_std_dvn']
        except KeyError:
            hist = self.get_histogram(variant)
            total = 0
            avg = self.get_histogram_avg(variant)
            for index, values in enumerate(hist):
                total += (index-avg)*(index-avg)*values
            self.dicts[variant]['histogram_std_dvn'] = (total/1024)**(0.5)
        return self.dicts[variant]['histogram_std_dvn']
    
    def get_hue_scalar(self):
        """Returns the scalar value for the averaged hue vector"""
        try:
            self.dicts[self.HUE][histogram_scalar]
        except KeyError:
            self.calc_hue_avg_vect()
        return self.dicts[self.HUE][histogram_scalar]
    
    def hist_avg(self, histogram):
        """Histograms can't use typical averaging"""
        weighted_total, total = 0, 0
        for index,values in enumerate(histogram):
            weighted_total += index*values
            total += values
        return (weighted_total/total)
    
    def calc_hue_avg_vect(self):
        """Returns the wrapped average, works in degrees"""
        x, y, total = 0, 0, 0
        for angle in range(256):
            if(histogram[angle] != 0):
                total += histogram[angle]
                x += math.sin(math.radians(angle))*histogram[angle]
                y += math.cos(math.radians(angle))*histogram[angle]
        self.dicts[self.HUE][histogram_avg] = math.degrees(math.atan(y/x))
        self.dicts[self.HUE][histogram_scalar] = ((x*x+y*y)**0.5)/total
        return self.dicts[self.HUE][histogram_avg]
    

    
    
#example = images("https://upload.wikimedia.org/wikipedia/commons/c/cd/DJ_Pauly_D_Crowd_%288417422634%29.jpg")
#print (example.get_histogram(example.GREEN))
#print (example.get_histogram(example.BLUE))
#print (example.get_histogram(example.RED))
#print (example.get_histogram(example.HUE))
#print (example.get_histogram(example.SATURATION))
#print (example.get_histogram(example.VALUE))
#print (example.get_histogram_avg(example.GREEN))
#print (example.get_histogram_avg(example.BLUE))
#print (example.get_histogram_avg(example.RED))
#print (example.get_histogram_avg(example.HUE))
#print (example.get_histogram_avg(example.SATURATION))
#print (example.get_histogram_avg(example.VALUE))
#print (example.get_histogram_std_dvn(example.GREEN))
#print (example.get_histogram_std_dvn(example.BLUE))
#print (example.get_histogram_std_dvn(example.RED))
#print (example.get_histogram_std_dvn(example.HUE))
#print (example.get_histogram_std_dvn(example.SATURATION))
#print (example.get_histogram_std_dvn(example.VALUE))
#print (example.get_HS_histogram())
#example.get_img(example.GREYSCALE)