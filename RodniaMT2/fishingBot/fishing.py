# load fishing.mp4 and loop it
import pyautogui
import pydirectinput
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
roi_left = fishingWindowLocation[0] + 35
roi_top = fishingWindowLocation[1] + 75
roi_width = 325
roi_height = 225

latestPositions = []
latestPositionLength = 5
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
    
    direction = 0
    # determine the direction in 360 degrees
    if len(latestPositions) > latestPositionLength:
        latestPositions.pop(0)
    latestPositions.append((x, y, w, h))
    if len(latestPositions) > 1:
        direction = np.arctan2(latestPositions[-1][1] - latestPositions[-2][1], latestPositions[-1][0] - latestPositions[-2][0]) * 180 / np.pi
        direction = (direction + 360) % 360
    
    # draw an arrow in the direction of the fish at the center of the screenshot and half the size of screenshot bigger
    cv2.arrowedLine(screenshot, (roi_width//2, roi_height//2), (roi_width//2 + int(roi_width//2 * np.cos(direction * np.pi / 180)), roi_height//2 + int(roi_height//2 * np.sin(direction * np.pi / 180))), (255, 255, 255), 2)    
    # draw a circle in the center of the fishingWindowLocation with radius 75
    circle_radius = 60
    cv2.circle(screenshot,  (roi_width//2, roi_height//2), circle_radius, (255, 255, 255), 2)

    # draw the biggest contour (c) in green
    cv2.rectangle(screenshot, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # draw a rectangle that is ahead of the fish in the direction of the fish by 50 pixels
    pixel_distance = 25
    offset_rectangle_points = [(x + int(pixel_distance * np.cos(direction * np.pi / 180)), y + int(pixel_distance * np.sin(direction * np.pi / 180))), (x+w + int(pixel_distance * np.cos(direction * np.pi / 180)), y+h + int(pixel_distance * np.sin(direction * np.pi / 180)))]
    cv2.rectangle(screenshot,offset_rectangle_points[0], offset_rectangle_points[1] , (255, 255, 255), 2)

    # check if both the fish and offset rectangle is inside the circle by approximating the circle with a square
    # if it is inside, then the fish is swimming towards the center of the circle
    # if it is outside, then the fish is swimming away from the center of the circle
    if x > roi_width//2 - circle_radius and x < roi_width//2 + circle_radius and y > roi_height//2 - circle_radius and y < roi_height//2 + circle_radius:
        print("swimming towards")
        pyautogui.moveTo(offset_rectangle_points[0][0] + roi_left, offset_rectangle_points[0][1] + roi_top)
        pyautogui.click()
        pyautogui.sleep(.5)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    cv2.imshow("screenshot", screenshot)
    cv2.waitKey(1)
