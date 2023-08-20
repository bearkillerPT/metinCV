import cv2
import numpy as np
import os

current_dir = os.path.dirname(os.path.abspath(__file__))

mask = cv2.imread(os.path.join(current_dir, "mask.png"))
mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
# find the biggest contour in the mask
cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
# find the countour with the biggest area bellow 500
cnts = sorted([cnt for cnt in cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
x, y, w, h = cv2.boundingRect(cnts[0])
# draw the biggest contour (c) in green
screenshot = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
cv2.rectangle(screenshot, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow("mask", screenshot)
cv2.waitKey()
