# load fishing.mp4 and loop it
import pyautogui
import pydirectinput
import cv2
import numpy as np
import win32gui

print("For this script please go the fishing location and start fishing, the bot will recognize the fishing window and start fishing")
bait_hotkey = '1'



circle_radius = 75

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


win32gui.EnumWindows(get_window_res_callback, None)
while client_box == [0, 0, 0, 0]:
    win32gui.EnumWindows(get_window_res_callback, None)
    pyautogui.sleep(1)
    continue
print("Client box: ", client_box)
pyautogui.sleep(1)

while True:
    pyautogui.sleep(2.5)
    print("Using bait (hotkey", bait_hotkey ,") and trying to start fishing")
    pydirectinput.press(bait_hotkey)
    pyautogui.sleep(1)
    pydirectinput.press("space", presses=2, interval=0.1)
    fishingWindowLocation = [
        client_box[0] + client_box[2]//2 - client_box[2] * 200 // 2073,
        client_box[1] + client_box[3]//2 - client_box[3] * 175 // 1211,
        client_box[2] * 400 // 2073, 
        client_box[3] * 380 // 1211
    ]
    roi = roi_left, roi_top, roi_width, roi_height = [
        fishingWindowLocation[2]* 1//10,
        fishingWindowLocation[3]* 17//64,
        fishingWindowLocation[2] * 4//5,
        fishingWindowLocation[3] * 5//10 
    ]
    latestPositions = []
    latestPositionLength = 2
    history_counter = 0
    windowPresent = False
    

    while not windowPresent:
        originalScreenshot = np.array(pyautogui.screenshot())
        fishingWindow = np.array(cv2.cvtColor(originalScreenshot[fishingWindowLocation[1]:fishingWindowLocation[1]+fishingWindowLocation[3], fishingWindowLocation[0]:fishingWindowLocation[0]+fishingWindowLocation[2]], cv2.COLOR_RGB2HSV))
        windowTopMask = cv2.inRange(fishingWindow, (4, 204, 43), (12, 233, 124))
        contours, _ = cv2.findContours(windowTopMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0 and cv2.contourArea(max(contours, key=cv2.contourArea)) > 1:
            windowPresent = True
        else:
            print("No fishing window detected, waiting for .25 second", end="\r")
        pyautogui.sleep(.25)

    while windowPresent:
        originalScreenshot = np.array(pyautogui.screenshot())
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
            
            circle_radius = 75

            # check if the center of the fish is inside the circle by approximating the circle with a square
            # if it is inside, then the fish is swimming towards the center of the circle
            # if it is outside, then the fish is swimming away from the center of the circle
            if x < roi_width and x > 0 and y < roi_height and y > 0: 
                if x > roi_width//2 - circle_radius and x < roi_width//2 + circle_radius and y > roi_height//2 - circle_radius and y < roi_height//2 + circle_radius:
                    print("swimming towards")
                    pyautogui.moveTo(
                            x + roi_left + fishingWindowLocation[0],
                            y + roi_top + fishingWindowLocation[1]
                    )
                    pyautogui.click()
                    rect_color = (255, 0, 0)
                    #pyautogui.sleep(0.1)

        fishingWindow = np.array(cv2.cvtColor(originalScreenshot[fishingWindowLocation[1]:fishingWindowLocation[1]+fishingWindowLocation[3], fishingWindowLocation[0]:fishingWindowLocation[0]+fishingWindowLocation[2]], cv2.COLOR_RGB2HSV))
        windowTopMask = cv2.inRange(fishingWindow, (4, 204, 43), (12, 233, 124))
        contours, _ = cv2.findContours(windowTopMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not (len(contours) > 0 and cv2.contourArea(max(contours, key=cv2.contourArea))) > 1:
            windowPresent = False
            break
    print("Fishing window can't be detected anymore, waiting for 1 second")