import cv2 as cv
import numpy as np
import pyautogui
import pydirectinput
from utils import useSkills, spamCapeAndSleep, waitForNextFloor, goToDungeon
import os
pyautogui.FAILSAFE = False

current_dir = os.getcwd()
boss_heathbar_image = current_dir + '\\images\\boss_heathbar.png'
blue_center_mask = lambda screenshot: cv.inRange(screenshot, np.array([0, 167, 111]), np.array([179, 255, 255]))
beran_setao_image = current_dir + '\\images\\beran_setao.png'
destroy_beran_setao_image = current_dir + '\\images\\destroy_beran_setao.png'


def find_dungeon_center(screenshot):
    screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_BGR2HSV)
    mask = blue_center_mask(screenshot)
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if contours:
        # find the closes contour to the center of the image and contour are > 1500
        selected_contour = None
        for contour in contours:
            area = cv.contourArea(contour)
            if area > 10000:
                selected_contour = contour
                break
        if selected_contour is None:
            print("No contour found!")
            return None
        x, y, w, h = cv.boundingRect(selected_contour)
        object_center_x = x + w // 2
        object_bottom_y = y + h
        print("Metin found! (", object_center_x, ", ", object_bottom_y, ") and area: ", area)
        return object_center_x, object_bottom_y
    else:
        print("No contour found!")
        return None
    
def locateHealthbarAndAttack():
    pydirectinput.keyDown('space')
    spamCapeAndSleep(1, False)
    pydirectinput.keyUp('space')
    return pyautogui.locateOnScreen(boss_heathbar_image, confidence=0.8)

def completeDungeon():
    goToDungeon(beran_setao_image, destroy_beran_setao_image)
    while (dungeon_center := find_dungeon_center(pyautogui.screenshot())) is None:
        pydirectinput.keyDown('q')
        pyautogui.sleep(.5)
        pydirectinput.keyUp('q')
        print('Dungeon center not found!')
        
    useSkills()
    pyautogui.moveTo(dungeon_center[0], dungeon_center[1], 0.2)
    pyautogui.click()
    pyautogui.sleep(2)
    
    print('Waiting for the boss healthbar')
    while locateHealthbarAndAttack() is None:
        pass
    print('Boss healthbar found! Imma kill it!')
    while locateHealthbarAndAttack():
        pass
    print('Boss healthbar dead!')
    pyautogui.press('z')
    
if __name__ == "__main__":
    pyautogui.sleep(1)
    completeDungeon()
    
    
    