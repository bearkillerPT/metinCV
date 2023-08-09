import pyautogui
import cv2 as cv
import numpy as np
import math

screenshot = pyautogui.screenshot()
screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2BGR)
roi_top_left_x = 0
roi_top_left_y = 250
roi_bottom_right_x = 2500
roi_bottom_right_y = 1100
cropped_screenshot = screenshot.astype('int32')[roi_top_left_y:roi_bottom_right_y, roi_top_left_x:roi_bottom_right_x]
lowest_distance = 100000
for distance in range(10, 100, 10):
    for threshold in range(5, 10, 1):
        current_mask = np.zeros(cropped_screenshot.shape, dtype=np.uint8)
        for i in range(len(current_mask)):
            for j in range(len(current_mask[i])):
                lowest_distance = (abs(cropped_screenshot[i][j][0] - cropped_screenshot[i][j][1]) + \
                    abs(cropped_screenshot[i][j][1] - cropped_screenshot[i][j][2]) + \
                    abs(cropped_screenshot[i][j][0] - cropped_screenshot[i][j][2]))/3
                if  lowest_distance < distance:
                    current_mask[i][j] = (255,255,255)
        metins = pyautogui.locateAllOnScreen("C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\metin_writing.png", confidence=.1*threshold, grayscale=True, region=[roi_top_left_x, roi_top_left_y, roi_bottom_right_x, roi_bottom_right_y])
        for metin in metins:
            print(metin)
            cv.rectangle(current_mask, (metin.left, metin.top), (metin.left + metin.width, metin.top + metin.height), (0, 0, 255), 5)
        cv.imshow('mask_' + str(distance), current_mask)
        cv.waitKey()
        cv.destroyAllWindows()
