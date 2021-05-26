# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 11:13:58 2020

@author: Tanishq Salkar
"""
import numpy as np
import cv2

# load the image, clone it for output, and then convert it to grayscale
image = cv2.imread('thresholding.jpg')
output = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# detect circles in the image
circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1.5, 20, param1=300, param2=25, minRadius=10, maxRadius=30)
print('Total number of circles: ', len(circles[0]))
# ensure at least some circles were found
if circles is not None:
    # convert the (x, y) coordinates and radius of the circles to integers
    circles = np.round(circles[0, :]).astype("int")
    for (x, y, r) in circles:
        h, s, v = hsv[y,x]
        if v>253:
            cv2.circle(output, (x, y), r, (255, 0, 0), 4)
        else:
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        

    # show the output image
    cv2.imshow("output", np.hstack([image, output]))
    cv2.waitKey(0)