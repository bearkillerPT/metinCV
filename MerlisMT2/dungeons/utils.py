import pyautogui
import pydirectinput
import pygetwindow as gw
import cv2 as cv
import numpy as np
import time
import os

current_dir = os.getcwd()
new_floor_image = current_dir + '\\images\\new_floor.png'
enter_dungeon_image = current_dir + '\\images\\enter_dungeon.png'
accept_enter_dungeon_image = current_dir + '\\images\\accept_enter_dungeon.png'

def getFormattedTime(seconds):
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"Finished in {minutes:02d}:{seconds:02d}"

def useSkills():
    print('Using skills!')
    pydirectinput.keyDown('ctrl')
    pyautogui.sleep(0.2)
    pydirectinput.press('h')
    pydirectinput.keyUp('ctrl')
    time.sleep(1)
    pydirectinput.press('3')
    time.sleep(2)
    pydirectinput.press('4')
    time.sleep(2)
    pydirectinput.keyDown('ctrl')
    pyautogui.sleep(0.2)
    pydirectinput.press('h')
    pydirectinput.keyUp('ctrl')

def spamCapeAndSleep(delay, checkNewFloor=True):
    start_time = time.time()
    while time.time() - start_time < delay:
        pydirectinput.press('2')
        pydirectinput.press('z')
        if checkNewFloor and pyautogui.locateOnScreen(new_floor_image, confidence=0.7):
            print('New floor detected!')
            break
        
def waitForNextFloor(maxDelay=None, waitForNextFloorImage=new_floor_image):
    start_time = time.time()
    while pyautogui.locateOnScreen(waitForNextFloorImage, confidence=0.7) is None:
        pyautogui.sleep(.1) 
        if maxDelay and time.time() - start_time > maxDelay:
            return False
    while pyautogui.locateOnScreen(new_floor_image, confidence=0.7):
        pyautogui.sleep(.1)
    print('New floor detected!')
    return True

def goToDungeon(dungeon_image, waitForNextFloorImage=new_floor_image):
    print("Clicking tab!")
    while (devil_tower_position := pyautogui.locateOnScreen(dungeon_image, confidence=0.6)) is None:
        pydirectinput.press('tab')
        pyautogui.sleep(.5)
    pyautogui.moveTo(devil_tower_position[0] + devil_tower_position[2]//2, devil_tower_position[1] + devil_tower_position[3]//2, 0.2)
    pyautogui.click()
    while (enter_dungeon_position := pyautogui.locateOnScreen(enter_dungeon_image, confidence=0.6)) is None:
        pyautogui.sleep(.1)
    pyautogui.moveTo(enter_dungeon_position[0] + enter_dungeon_position[2]//2, enter_dungeon_position[1] + enter_dungeon_position[3]//2, 0.2)
    pyautogui.click()
    while (accept_enter_dungeon_position := pyautogui.locateOnScreen(accept_enter_dungeon_image, confidence=0.6)) is None:
        pyautogui.sleep(.1)
    pyautogui.moveTo(accept_enter_dungeon_position[0] + accept_enter_dungeon_position[2]//2, accept_enter_dungeon_position[1] + accept_enter_dungeon_position[3]//2, 0.2)
    pyautogui.click()
    print("Dungeon clicked... waiting for the first floor to start")
    waitForNextFloor(None, waitForNextFloorImage)
    
def addBlackRectangleOnTopOfThePlayer(screenshot):
    client_box = gw.getWindowsWithTitle('Merlis')[0]

    centerRectangle = {
        "left": client_box.left + client_box.width // 2 - 175,
        "top": client_box.top + client_box.height // 2 - 100,
        "width": 250,
        "height": 200
    }  

    # Make sure the image is cast to numpy array
    screenshot = np.array(screenshot)
    screenshot[centerRectangle["top"]:centerRectangle["top"] + centerRectangle["height"], centerRectangle["left"]:centerRectangle["left"] + centerRectangle["width"]] = 0

    return screenshot