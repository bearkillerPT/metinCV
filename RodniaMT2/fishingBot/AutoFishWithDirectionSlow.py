# load fishing.mp4 and loop it
import pyautogui
import pydirectinput
import cv2
import numpy as np
import os 
import win32gui


client_box = [0, 0, 0, 0]

def get_window_res_callback(hwnd, extra):
    global client_box
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    window_name = win32gui.GetWindowText(hwnd)
    if window_name == 'Rodnia - The King\'s Return':
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
    roi_width = client_box[2] * 325 // 2073 
    roi_height = client_box[3] * 250 // 1211
    print("roi: ", roi_left, roi_top, roi_width, roi_height)
    latestPositions = []
    latestPositionLength = 2
    history_counter = 0
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
            
            direction = 0
            # determine the direction in 360 degrees
            if len(latestPositions) > latestPositionLength:
                latestPositions.pop(0)
            latestPositions.append((x, y, w, h))
            history_counter += 1

            if len(latestPositions) > 1:
                direction = np.arctan2(latestPositions[-1][1] - latestPositions[-2][1], latestPositions[-1][0] - latestPositions[-2][0]) * 180 / np.pi
                direction = (direction + 360) % 360
            # draw a rectangle that is ahead of the fish in the direction of the fish by 50 pixels
            pixel_distance = 25
            offset_rectangle_points = [(x + int(pixel_distance * np.cos(direction * np.pi / 180)), y + int(pixel_distance * np.sin(direction * np.pi / 180))), (x+w + int(pixel_distance * np.cos(direction * np.pi / 180)), y+h + int(pixel_distance * np.sin(direction * np.pi / 180)))]
            rect_color = (255, 255, 255)
            circle_radius = 75
            window_center = (roi_width, roi_height + 40)

            # check if the center of the fish is inside the circle by approximating the circle with a square
            # if it is inside, then the fish is swimming towards the center of the circle
            # if it is outside, then the fish is swimming away from the center of the circle
            if offset_rectangle_points[0][0] < roi_width and offset_rectangle_points[0][0] > 0 and offset_rectangle_points[0][1] < roi_height and offset_rectangle_points[0][1] > 0: 
                if offset_rectangle_points[0][0] > roi_width//2 - circle_radius and offset_rectangle_points[0][0] < roi_width//2 + circle_radius and offset_rectangle_points[0][1] > roi_height//2 - circle_radius and offset_rectangle_points[0][1] < roi_height//2 + circle_radius:
                    if history_counter > latestPositionLength - 1:
                        print("swimming towards")
                        pyautogui.moveTo(offset_rectangle_points[0][0] + roi_left, offset_rectangle_points[0][1] + roi_top)
                        pyautogui.click()
                        rect_color = (255, 0, 0)
                        history_counter = 0


            # draw an arrow in the direction of the fish at the center of the screenshot and half the size of screenshot bigger
            #cv2.arrowedLine(screenshot, (window_center[0]//2, window_center[1]//2), (window_center[0]//2 + int(window_center[0]//2 * np.cos(direction * np.pi / 180)), window_center[1]//2 + int(window_center[1]//2 * np.sin(direction * np.pi / 180))), (255, 255, 255), 2)    
            ## draw a circle in the center of the fishingWindowLocation with radius 75
            #cv2.circle(screenshot,  (window_center[0]//2, window_center[1]//2), circle_radius, (255, 255, 255), 2)
            #pyautogui.sleep(.01)
#
            ## draw the biggest contour (c) in green
            #cv2.rectangle(screenshot, (x, y), (x+w, y+h), (0, 255, 0), 2)        
#
            #cv2.rectangle(screenshot,offset_rectangle_points[0], offset_rectangle_points[1] , rect_color, 2)
            #screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            #winname = "screenshot"
            ##screenshot = cv2.resize(screenshot, (screenshot.shape[1]*2, screenshot.shape[0]*2))
            ##cv2.namedWindow(winname)   
            ##cv2.moveWindow(winname, 0,0)
            #cv2.imshow(winname, screenshot)
            #cv2.waitKey(1)
            fishingWindowLocation = pyautogui.locateOnScreen(fishingWindow, confidence=0.7)
    print("Fishing window can't be detected anymore, waiting for 1 second")