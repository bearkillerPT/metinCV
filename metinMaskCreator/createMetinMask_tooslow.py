import cv2 as cv
import numpy as np
import pyautogui

metin_image = cv.imread('C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\metin.png')

colors = []

for i in range(len(metin_image)):
    for j in range(len(metin_image[i])):
        if metin_image[i][j][0] > 0 and metin_image[i][j][1] > 0 and metin_image[i][j][2] > 0:
            colors.append(metin_image[i][j].tolist())

count_threshold = 3
most_common_colors = [item for item in colors if colors.count(item) >= count_threshold]
# remove duplicates
most_common_colors = [str(list(t)) for t in set(tuple(element) for element in most_common_colors)]

print(most_common_colors)

#screenshot = cv.imread('C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\res.png')
screenshot = pyautogui.screenshot()
screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_BGR2HSV)
        
roi_top_left_x = 0
roi_top_left_y = 350
roi_bottom_right_x = 2050
roi_bottom_right_y = 1080
cropped_screenshot = screenshot[roi_top_left_y:roi_bottom_right_y, roi_top_left_x:roi_bottom_right_x]

# create a mask with the most common colors

mask = np.zeros(cropped_screenshot.shape, dtype=np.uint8)

for i in range(len(mask)):
    for j in range(len(mask[i])):
        if str(cropped_screenshot[i][j].tolist()) in most_common_colors:
            mask[i][j] = (255,255,255)

print("done")
# show the mask and save it
cv.imshow('mask', cv.cvtColor(cropped_screenshot, cv.COLOR_HSV2RGB))
cv.waitKey()