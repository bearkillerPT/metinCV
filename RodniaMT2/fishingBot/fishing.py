# load fishing.mp4 and loop it
import pyautogui
import cv2
import numpy as np
import os 

current_dir = os.path.dirname(os.path.abspath(__file__))
fishingWindow = cv2.imread(os.path.join(current_dir, "images/fishingWindow.png"))
fishingWindowLocation = pyautogui.locateOnScreen(fishingWindow, confidence=0.7)
while fishingWindowLocation is None:
    fishingWindowLocation = pyautogui.locateOnScreen(fishingWindow, confidence=0.7)
    pyautogui.sleep(.5)
print(fishingWindowLocation)
# loop video
roi_left = fishingWindowLocation[0] + 35
roi_top = fishingWindowLocation[1] + 75
roi_width = 325
roi_height = 250
while True:
    screenshot = np.array(pyautogui.screenshot())[roi_top:roi_top+roi_height, roi_left:roi_left+roi_width]
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_screenshot = cv2.cvtColor(gray_screenshot, cv2.COLOR_GRAY2BGR)
    gray_screenshot = cv2.cvtColor(gray_screenshot, cv2.COLOR_BGR2HSV)

    lower_fish = np.array([0, 0, 79])
    upper_fish = np.array([179, 255, 96])

    mask = cv2.inRange(gray_screenshot, lower_fish, upper_fish)

    # find the biggest contour in the mask
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    # find the countour with the biggest area
    #cnts = sorted([cnt for cnt in cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]
    x, y, w, h = cv2.boundingRect(cnts[0])
    # draw the biggest contour (c) in green
    cv2.rectangle(screenshot, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    #cv2.imwrite("screenshot.png", screenshot)
    #cv2.imwrite("mask.png", mask)

    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    cv2.imshow("screenshot", screenshot)
    cv2.waitKey(1)
