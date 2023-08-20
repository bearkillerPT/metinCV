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

direction = 0
# determine the direction in 360 degrees
# determin if the width or height is bigger
# if width is bigger, then the fish is swimming left or right with a 50% margin
# if height is bigger, then the fish is swimming up or down with a 50% margin
# the sense of the swim is determined by the side containing the biggest contour
# the margin by the side, in the opposite direction of the swim, containing the second biggest contour
if w > h:
    left_half = mask[y:y+h, x:x+w//2]
    right_half = mask[y:y+h, x+w//2:x+w]
    left_half_cnts, _ = cv2.findContours(left_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    right_half_cnts, _ = cv2.findContours(right_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    left_half_cnts = sorted([cnt for cnt in left_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    right_half_cnts = sorted([cnt for cnt in right_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    if len(left_half_cnts) > 0 and len(right_half_cnts) > 0:
        if cv2.contourArea(left_half_cnts[0]) > cv2.contourArea(right_half_cnts[0]):
            direction = 270
        else:
            direction = 90
    
    upper_half = mask[y:y+h//2, x:x+w]
    lower_half = mask[y+h//2:y+h, x:x+w]
    upper_half_cnts, _ = cv2.findContours(upper_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lower_half_cnts, _ = cv2.findContours(lower_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    upper_half_cnts = sorted([cnt for cnt in upper_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    lower_half_cnts = sorted([cnt for cnt in lower_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    # use the vertical information to adjust the angle in a percentage of 50%
    if len(upper_half_cnts) > 0 and len(lower_half_cnts) > 0:
        if cv2.contourArea(upper_half_cnts[0]) > cv2.contourArea(lower_half_cnts[0]):
            direction += 15
        else:
            direction -= 15
else:
    upper_half = mask[y:y+h//2, x:x+w]
    lower_half = mask[y+h//2:y+h, x:x+w]
    upper_half_cnts, _ = cv2.findContours(upper_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    lower_half_cnts, _ = cv2.findContours(lower_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    upper_half_cnts = sorted([cnt for cnt in upper_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    lower_half_cnts = sorted([cnt for cnt in lower_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    if len(upper_half_cnts) > 0 and len(lower_half_cnts) > 0:
        if cv2.contourArea(upper_half_cnts[0]) > cv2.contourArea(lower_half_cnts[0]):
            direction = 0
        else:
            direction = 180
    
    left_half = mask[y:y+h, x:x+w//2]
    right_half = mask[y:y+h, x+w//2:x+w]
    left_half_cnts, _ = cv2.findContours(left_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    right_half_cnts, _ = cv2.findContours(right_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    left_half_cnts = sorted([cnt for cnt in left_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    right_half_cnts = sorted([cnt for cnt in right_half_cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    # use the horizontal information to adjust the angle in a percentage of 50%
    if len(left_half_cnts) > 0 and len(right_half_cnts) > 0:
        if cv2.contourArea(left_half_cnts[0]) > cv2.contourArea(right_half_cnts[0]):
            direction += 15
        else:
            direction -= 15

print(direction)

# draw an arrow in the direction of the fish
cv2.arrowedLine(mask, (x+w//2, y+h//2), (x+w//2+int(100*np.cos(np.deg2rad(direction))), y+h//2+int(100*np.sin(np.deg2rad(direction)))), (255, 255, 255), 2)

# draw the biggest contour (c) in green
screenshot = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
cv2.rectangle(screenshot, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow("mask", screenshot)
cv2.waitKey()
