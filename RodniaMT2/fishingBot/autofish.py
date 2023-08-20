# load fishing.mp4 and loop it
import pyautogui
import pydirectinput
import cv2
import numpy as np
import os 

print("For this script please go the fishing location and start fishing, the bot will recognize the fishing window and start fishing")
bait_hotkey = '1'



current_dir = os.path.dirname(os.path.abspath(__file__))
fishingWindow = cv2.imread(os.path.join(current_dir, "images/fishingWindow.png"))
pyautogui.sleep(1)
while True:
    pyautogui.sleep(2.5)
    print("Using bait (hotkey", bait_hotkey ,") and trying to start fishing")
    pydirectinput.press(bait_hotkey)
    pyautogui.sleep(1)
    pydirectinput.press("space", presses=2, interval=0.1)
    fishingWindowLocation = pyautogui.locateOnScreen(fishingWindow, confidence=0.7)
    while fishingWindowLocation is None:
        fishingWindowLocation = pyautogui.locateOnScreen(fishingWindow, confidence=0.7)
        pyautogui.sleep(1)
    print("Fishing window detected at: ", fishingWindowLocation)
    roi_left = fishingWindowLocation[0] + 35
    roi_top = fishingWindowLocation[1] + 75
    roi_width = 325
    roi_height = 225

    while fishingWindowLocation is not None:
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
        if cv2.contourArea(cnts[0]) > 1:
            x, y, w, h = cv2.boundingRect(cnts[0])
            
            circle_radius = 75
            window_center = (roi_width, roi_height + 40)

            # check if the center of the fish is inside the circle by approximating the circle with a square
            # if it is inside, then the fish is swimming towards the center of the circle
            # if it is outside, then the fish is swimming away from the center of the circle
            if x < roi_width and x > 0 and y < roi_height and y > 0: 
                if x > roi_width//2 - circle_radius and x < roi_width//2 + circle_radius and y > roi_height//2 - circle_radius and y < roi_height//2 + circle_radius:
                    print("swimming towards")
                    pyautogui.moveTo(x  + roi_left, y  + roi_top)
                    pyautogui.click()
                    rect_color = (255, 0, 0)
                    pyautogui.sleep(.1)

            fishingWindowLocation = pyautogui.locateOnScreen(fishingWindow, confidence=0.7)
    print("Fishing window can't be detected anymore, waiting for 1 second")