# load fishing.mp4 and loop it
import pyautogui
import pydirectinput
import cv2
import numpy as np
import win32gui
import os
import time
from CaptchaSolver import CaptchaSolver

cwd = os.getcwd()
window_header_image = cwd + '\\images\\fishingWindow.png'
captcha = cwd + '..\\images\\captcha.png'


circle_radius = 70

client_box = [0, 0, 0, 0]

def get_window_res_callback(hwnd, extra):
    global client_box
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    window_name = win32gui.GetWindowText(hwnd)
    if window_name == 'Merlis':
        print("Window %s:" % window_name)
        print("\tLocation: (%d, %d)" % (x, y))
        print("\t    Size: (%d, %d)" % (w, h))
        if x < 20:
            x = 20
        if y < 20:
            y = 20
        client_box = [x, y, w, h]



print("For this script please go the fishing location and start fishing, the bot will recognize the fishing window and start fishing")
bait_hotkey = '1'

win32gui.EnumWindows(get_window_res_callback, None)
while client_box == [0, 0, 0, 0]:
    win32gui.EnumWindows(get_window_res_callback, None)
    pyautogui.sleep(1)
    continue
print("Client box: ", client_box)
while True:
    pyautogui.sleep(3)
    print("Using bait (hotkey", bait_hotkey ,") and trying to start fishing")
    pydirectinput.press(bait_hotkey)
    pyautogui.sleep(1)
    pydirectinput.press("space", presses=2, interval=0.1)
    window_header_search_start_time = time.time()
    while (window_header_location := pyautogui.locateOnScreen(window_header_image, confidence=0.8)) is None:
        pyautogui.sleep(.1)
        if time.time() - window_header_search_start_time > 5:
            # check for a captcha
            if pyautogui.locateOnScreen(captcha, confidence=0.8):
                (_, captcha_box), _, _ = CaptchaSolver.solve(screenshot)
                # move to the center of the captcha box
                pyautogui.moveTo(captcha_box[2] + (captcha_box[3] - captcha_box[2])//2, captcha_box[0] + (captcha_box[1] - captcha_box[0])//2)
                pyautogui.sleep(.1)
                pyautogui.click()
        
    fishingWindowLocation = [
        window_header_location.left,
        window_header_location.top,
        400, 
        380
    ]
    roi = roi_left, roi_top, roi_width, roi_height = [
        fishingWindowLocation[2]* 1//10,
        fishingWindowLocation[3]* 17//64,
        fishingWindowLocation[2] * 4//5,
        fishingWindowLocation[3] * 5//10 
    ]
    latestPositions = []
    latestPositionLength = 3
    history_counter = 0
    windowPresent = False
    firstTryTime = pyautogui.time.time()
    while not windowPresent:
        originalScreenshot = np.array(pyautogui.screenshot())
        fishingWindow = np.array(cv2.cvtColor(originalScreenshot[fishingWindowLocation[1]:fishingWindowLocation[1]+fishingWindowLocation[3], fishingWindowLocation[0]:fishingWindowLocation[0]+fishingWindowLocation[2]], cv2.COLOR_RGB2HSV))
        windowTopMask = cv2.inRange(fishingWindow, (4, 204, 43), (12, 233, 124))
        contours, _ = cv2.findContours(windowTopMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if (currentTime := pyautogui.time.time()) - firstTryTime > 15:
            print("Seems the window is taking too long... pressing Space and trying again")
            pydirectinput.press("space")
            pyautogui.sleep(1)
            firstTryTime = currentTime
            continue
        if len(contours) > 0 and cv2.contourArea(max(contours, key=cv2.contourArea)) > 1:
            windowPresent = True
        else:
            print("No fishing window detected, waiting for .25 second", end="\r")
        pyautogui.sleep(.1)

    while windowPresent:
        screenshot = originalScreenshot[fishingWindowLocation[1]:fishingWindowLocation[1]+fishingWindowLocation[3], fishingWindowLocation[0]:fishingWindowLocation[0]+fishingWindowLocation[2]]
        fishingWindow = screenshot[roi_top:roi_top+roi_height, roi_left:roi_left+roi_width]
        gray_screenshot = cv2.cvtColor(fishingWindow, cv2.COLOR_RGB2GRAY)
        gray_screenshot = cv2.cvtColor(gray_screenshot, cv2.COLOR_GRAY2BGR)
        filtered_screenshot = cv2.cvtColor(gray_screenshot, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(filtered_screenshot, np.array([0, 0, 79]), np.array([179, 255, 96]))

        # find the biggest contour in the mask
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
        # find the countour with the biggest area
        #cnts = sorted([cnt for cnt in cnts if cv2.contourArea(cnt) < 300], key=cv2.contourArea, reverse=True)[:1]
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]
        if cv2.contourArea(cnts[0]) > 1:
            x, y, w, h = cv2.boundingRect(cnts[0])
            
            direction = 0
            # determine the direction in 360 degrees
            if len(latestPositions) > latestPositionLength:
                latestPositions.pop(0)
            latestPositions.append((x, y, w, h))

            if len(latestPositions) > 1:
                direction = np.arctan2(latestPositions[-1][1] - latestPositions[-2][1], latestPositions[-1][0] - latestPositions[-2][0]) * 180 / np.pi
                direction = (direction + 360) % 360
            # draw a rectangle that is ahead of the fish in the direction of the fish by 50 pixels
            pixel_distance = 25
            offset_rectangle_points = [(x + int(pixel_distance * np.cos(direction * np.pi / 180)), y + int(pixel_distance * np.sin(direction * np.pi / 180))), (x+w + int(pixel_distance * np.cos(direction * np.pi / 180)), y+h + int(pixel_distance * np.sin(direction * np.pi / 180)))]
            rect_color = (255, 255, 255)
            history_counter += 1

            # check if the center of the fish is inside the circle by approximating the circle with a square
            # if it is inside, then the fish is swimming towards the center of the circle
            # if it is outside, then the fish is swimming away from the center of the circle
            if offset_rectangle_points[0][0] < roi_width and offset_rectangle_points[0][0] > 0 and offset_rectangle_points[0][1] < roi_height and offset_rectangle_points[0][1] > 0:
                if offset_rectangle_points[0][0] > roi_width//2 - circle_radius and offset_rectangle_points[0][0] < roi_width//2 + circle_radius and offset_rectangle_points[0][1] > roi_height//2 - circle_radius and offset_rectangle_points[0][1] < roi_height//2 + circle_radius:
                    if history_counter > latestPositionLength - 1:
                        print("swimming towards")
                        pyautogui.moveTo(
                            offset_rectangle_points[0][0] + roi_left + fishingWindowLocation[0],
                            offset_rectangle_points[0][1] + roi_top + fishingWindowLocation[1]
                        )
                        pyautogui.click()
                        rect_color = (255, 0, 0)
                        history_counter = 0

            fishingWindow = cv2.cvtColor(fishingWindow, cv2.COLOR_HSV2BGR)
            # draw an arrow in the direction of the fish at the center of the screenshot and half the size of screenshot bigger
            cv2.arrowedLine(fishingWindow, (roi_width//2, roi_height//2), (roi_width//2 + int(roi_width//2 * np.cos(direction * np.pi / 180)), roi_height//2 + int(roi_height//2 * np.sin(direction * np.pi / 180))), (255, 255, 255), 2)    
            # draw a circle in the center of the fishingWindowLocation with radius 75
            cv2.circle(fishingWindow,  (roi_width//2, roi_height//2), circle_radius, (255, 255, 255), 2)

            # draw the biggest contour (c) in green
            cv2.rectangle(fishingWindow, (x, y), (x+w, y+h), (0, 255, 0), 2)        

            cv2.rectangle(fishingWindow,offset_rectangle_points[0], offset_rectangle_points[1] , rect_color, 2)
            winname = "fishingWindow"
            #screenshot = cv2.resize(screenshot, (screenshot.shape[1]*2, screenshot.shape[0]*2))
            #cv2.namedWindow(winname)   
            #cv2.moveWindow(winname, 0,0)
            cv2.imwrite('screenshot.png', cv2.cvtColor(fishingWindow, cv2.COLOR_HSV2BGR))
            cv2.imwrite('mask.png', cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))
            #cv2.waitKey(1)
            originalScreenshot = np.array(pyautogui.screenshot())
            fishingWindow = np.array(cv2.cvtColor(originalScreenshot[fishingWindowLocation[1]:fishingWindowLocation[1]+fishingWindowLocation[3], fishingWindowLocation[0]:fishingWindowLocation[0]+fishingWindowLocation[2]], cv2.COLOR_RGB2HSV))
            windowTopMask = cv2.inRange(fishingWindow, (4, 204, 43), (12, 233, 124))
            contours, _ = cv2.findContours(windowTopMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not (len(contours) > 0 and cv2.contourArea(max(contours, key=cv2.contourArea))) > 1:
                windowPresent = False
                break
            
    print("Fishing window can't be detected anymore, waiting for 1 second")