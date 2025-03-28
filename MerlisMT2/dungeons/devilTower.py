import pyautogui
import pydirectinput
import cv2 as cv
import numpy as np
import os
import pygetwindow as gw
import time
from utils import useSkills, spamCapeAndSleep, waitForNextFloor, goToDungeon, addBlackRectangleOnTopOfThePlayer, safe_locate_on_screen
from functionTimer import call_with_timeout

current_dir = os.getcwd()
boss_heathbar_image = current_dir + '\\images\\boss_heathbar.png'
new_floor_image = current_dir + '\\images\\new_floor.png'
demon_king_end_image = current_dir + '\\images\\demon_king_end.png'
key_stone_image = current_dir + '\\images\\key_stone.png'
zin_bong_in_key_image = current_dir + '\\images\\zin_bong_in_key.png'
devil_tower_image = current_dir + '\\images\\devil_tower.png'
enter_dungeon_image = current_dir + '\\images\\enter_dungeon.png'
accept_enter_dungeon_image = current_dir + '\\images\\accept_enter_dungeon.png'

client_box = gw.getWindowsWithTitle('Merlis')[0]

metin_of_toughness_mask = lambda screenshot: cv.inRange(screenshot, np.array([129, 74, 53]), np.array([145, 187, 255]))
metin_of_death_mask = lambda screenshot: cv.inRange(screenshot, np.array([114, 0, 0]), np.array([166, 102, 205]))
metin_of_murder_mask = lambda screenshot: cv.inRange(screenshot, np.array([121, 0, 43]), np.array([179, 75, 174]))

client = {"client_id" : 0,
        "healthbar": [
            client_box.left + 200 * client_box.width // 2073,
            client_box.top + 300 * client_box.height // 2550,
            client_box.width - 25 * client_box.width // 2073,
            client_box.height - 125 * client_box.height // 1850
        ],
        "window_top": (client_box.left, client_box.top)
}

def findDungeonCenter(screenshot):
    mask = cv.inRange(screenshot, np.array([112, 192, 79]), np.array([122, 239, 146]))
    # blur the colors by a factor of 100
    mask = cv.blur(mask, (100, 100))
    return mask

def findContour(screenshot, applyMask, area_range=(300, 10000)):
    hsv_screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_BGR2HSV)
    hsv_screenshot = addBlackRectangleOnTopOfThePlayer(hsv_screenshot)
    roi_top_left_x = client["healthbar"][0] 
    roi_top_left_y =   client["healthbar"][1] 
    roi_bottom_right_x = client["healthbar"][2] - 200
    roi_bottom_right_y =    client["healthbar"][3]
    cropped_screenshot = hsv_screenshot[roi_top_left_y:roi_bottom_right_y, roi_top_left_x:roi_bottom_right_x]
    mask = applyMask(cropped_screenshot)
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if contours:
        # find the closes contour to the center of the image and contour are > 1500
        selected_contour = None
        for contour in contours:
            area = cv.contourArea(contour)
            if area > area_range[0] and area < area_range[1]:
                selected_contour = contour
                break
        if selected_contour is None:
            return None
        x, y, w, h = cv.boundingRect(selected_contour)
        object_center_x = x + w // 2 + roi_top_left_x
        object_center_y = y + h // 2 + roi_top_left_y
        # draw a rectangle around the detected object
        cv.rectangle(cropped_screenshot, (x, y), (x + w, y + h), (255, 255, 255), 2,)
        cv.imwrite("res.png", cv.cvtColor(cropped_screenshot, cv.COLOR_HSV2RGB))
        cv.imwrite("mask.png", mask)
        print('Metin found! (x:', str(object_center_x)+ ',y:', object_center_y,'\), area:', area)
        return object_center_x, object_center_y 
    return None

def walkToDungeonCenter(area=(50000, 1000000)):
    while (center := findContour(pyautogui.screenshot(), findDungeonCenter, area_range=area)) is None:
        print('Looking for the center of the dungeon...')
        pydirectinput.keyDown('q')
        pyautogui.sleep(.275) 
        pydirectinput.keyUp('q')
    pyautogui.moveTo(center[0], center[1], 0.2)
    pyautogui.click()
    pyautogui.sleep(3)

def walkAround(invertedCamera=False):
    cameraKey = 'e' if invertedCamera else 'q'
    pydirectinput.keyDown(cameraKey)
    pyautogui.sleep(.125)
    pydirectinput.keyUp(cameraKey)
    pydirectinput.keyDown('w')
    spamCapeAndSleep(.375)
    pydirectinput.keyUp('w')

def firstFloor():
    waitForNextFloor()
    walkToDungeonCenter()
    pydirectinput.keyDown('e')
    pyautogui.sleep(.3)
    pydirectinput.keyUp('e')
    pydirectinput.keyDown('w')
    pyautogui.sleep(1)
    pydirectinput.keyUp('w')
    pydirectinput.keyDown('q')
    pyautogui.sleep(.2)
    pydirectinput.keyUp('q')
    while (metin_position := findContour(pyautogui.screenshot(), metin_of_toughness_mask, (350, 10000))) is None:
        pydirectinput.keyDown('q')
        pyautogui.sleep(.4)
        pydirectinput.keyUp('q')
        pydirectinput.keyDown('w')
        pyautogui.sleep(1.5)
        pydirectinput.keyUp('w')
        print('Metin is not on the screen!', metin_position)
    
    pyautogui.moveTo(metin_position[0], metin_position[1], 0.2)
    pyautogui.click()
    
    print('Metin is dead!')
    farming_start_time = time.time()
    while not waitForNextFloor(5):
        print('New floor not detected!')
        if time.time() - farming_start_time > 10:
            pydirectinput.keyDown('a')
            pyautogui.sleep(.5)
            pydirectinput.keyUp('a')
    print ('New floor starting!')
    
def secondFloor():
    walkToDungeonCenter()
    while True:
        for i in range(3):
            walkAround()
            pydirectinput.press('2')
        pydirectinput.keyDown('space')
        spamCapeAndSleep(10)
        pydirectinput.keyUp('space')
        if safe_locate_on_screen(new_floor_image, confidence=0.7):
            print('New floor detected!')
            break
    
def thirdFloor():
    walkToDungeonCenter()
    key_stones_clicked = 0
    while key_stones_clicked < 5:
        pydirectinput.keyDown('space')
        spamCapeAndSleep(.5)
        pydirectinput.keyUp('space')
        if key_stone := safe_locate_on_screen(key_stone_image, confidence=0.7):
            print('Key Stone found!')
            key_stones_clicked += 1
            pyautogui.moveTo(key_stone[0] + key_stone[2]//2, key_stone[1] + key_stone[3]//2, 0.2)
            pyautogui.click(button='right')
            pyautogui.moveTo(key_stone[0] + key_stone[2]//2-250, key_stone[1] + key_stone[3]//2, 0.2)
            pyautogui.sleep(.2) # wait for the item to disappear
    while safe_locate_on_screen(new_floor_image, confidence=0.7) is None:
        pyautogui.sleep(.1)

def forthFloor():
    walkToDungeonCenter()
    while True:
        walkAround()
        pydirectinput.keyDown('space')
        spamCapeAndSleep(3.3)
        pydirectinput.keyUp('space')
        pydirectinput.press('z')
        if safe_locate_on_screen(demon_king_end_image, confidence=0.6):
            print('Demon king must be dead!')
            pyautogui.sleep(4)
            break
    
def fifthFloor():
    for i in range(4):
        while (metin_location := findContour(pyautogui.screenshot(), metin_of_death_mask, (450, 1200))) is None:
            pydirectinput.keyDown('q')
            pyautogui.sleep(.2)
            pydirectinput.keyUp('q')
            pydirectinput.keyDown('w')
            pyautogui.sleep(.2)
            pydirectinput.keyUp('w')
            print('Metin is not on the screen!', metin_location)
        print('Metin found!', metin_location)
        pyautogui.moveTo(metin_location[0], metin_location[1], 0.2)
        pyautogui.click()
        waiting_for_metin_timer = time.time()
        real_metin = True
        while safe_locate_on_screen(boss_heathbar_image, confidence=0.8) is None:
            pyautogui.sleep(.1)
            if time.time() - waiting_for_metin_timer > 30:
                pyautogui.press('z')
                real_metin = False
                break
        if real_metin:
            start_farming_timer = time.time()
            while safe_locate_on_screen(boss_heathbar_image, confidence=0.8):
                if(time.time() - start_farming_timer > 5):
                    pydirectinput.keyDown('a')
                    pyautogui.sleep(.1)
                    pydirectinput.keyUp('a')
                pyautogui.sleep(.1)
                #print('Metin is still alive!')
            pydirectinput.press('z')
            pyautogui.sleep(4)
    
def sixthFloor():
    pyautogui.sleep(4)
    for i in range(4):
        while (metin_location := findContour(pyautogui.screenshot(), metin_of_murder_mask, (350, 1200))) is None:
            pydirectinput.keyDown('q')
            pyautogui.sleep(.2)
            pydirectinput.keyUp('q')
            pydirectinput.keyDown('w')
            pyautogui.sleep(.2)
            pydirectinput.keyUp('w')
            print('Metin is not on the screen!', metin_location)
        print('Metin found!', metin_location)
        pyautogui.moveTo(metin_location[0], metin_location[1], 0.2)
        pyautogui.click()
        waiting_for_metin_timer = time.time()
        real_metin = True
        while safe_locate_on_screen(boss_heathbar_image, confidence=0.8) is None:
            pyautogui.sleep(.1)
            if time.time() - waiting_for_metin_timer > 30:
                real_metin = False
                break
        if real_metin:
            start_farming_timer = time.time()
            while safe_locate_on_screen(boss_heathbar_image, confidence=0.8):
                if(time.time() - start_farming_timer > 5):
                    pydirectinput.keyDown('a')
                    pyautogui.sleep(.1)
                    pydirectinput.keyUp('a')
                pyautogui.sleep(.1)
            pydirectinput.press('z')
            pyautogui.sleep(4)
    while safe_locate_on_screen(new_floor_image, confidence=0.8) is None: 
        pyautogui.sleep(.1)
        
def seventhFloor():
    walkToDungeonCenter()
    while (zin_bong := safe_locate_on_screen(zin_bong_in_key_image, confidence=0.8)) is None:
        print('Zin Bong not found!')
        pydirectinput.keyDown('space')
        spamCapeAndSleep(.5)
        pydirectinput.keyUp('space')

    print('Zin Bong found!')
    pyautogui.moveTo(zin_bong[0] + zin_bong[2]//2, zin_bong[1] + zin_bong[3]//2, 0.2)
    pyautogui.click(button='right')
    waitForNextFloor()

def eigthFloor(dungeon_start_time):
    walkToDungeonCenter((5000, 100000))
    was_boss_found = False
    farming_start_time = time.time()
    #if farming_start_time - dungeon_start_time < 7*60: 
    #    print(f"Sleeping for {getFormattedTime(farming_start_time - dungeon_start_time)} until 8:30m have passed since the dungeon started (to avoid teleporting to the 1st city after 2 minutes)")
    #    pyautogui.sleep(7*60 - farming_start_time + dungeon_start_time)
    useSkills()
    while True:
        if not safe_locate_on_screen(boss_heathbar_image, confidence=0.8):
            if not was_boss_found and (time.time() - farming_start_time) > 4:
                walkAround(True)
                farming_start_time = time.time()
        else:
            was_boss_found = True
        pydirectinput.keyDown('space')
        spamCapeAndSleep(2)
        pydirectinput.keyUp('space')
        pyautogui.sleep(.5)
        if was_boss_found and safe_locate_on_screen(boss_heathbar_image, confidence=0.8) is None:
            print('Boss fight ended!')
            pydirectinput.press('z')
            break

def timeoutDungeon():
    dungeon_start_time = time.time()
    useSkills()
    firstFloor()
    secondFloor()
    pydirectinput.press('i')
    thirdFloor()
    pydirectinput.press('i')
    forthFloor()
    fifthFloor()
    sixthFloor()
    pydirectinput.press('i')
    seventhFloor()
    eigthFloor(dungeon_start_time)
    
def completeDungeon():
    goToDungeon(devil_tower_image)
    start_time = time.time()
    call_with_timeout(timeoutDungeon, timeout=11 * 60)
    return time.time() - start_time
    

if __name__ == '__main__':
    # You should have the inventory open!
    pyautogui.sleep(1)
    print('Welcome to the Devil\'s Tower!')
    while True:        
        start_time = time.time()
        try:
            completeDungeon()
        except Exception as e:
            print(e)
        timeDiff = time.time() - start_time

        print(f"Total time: {int(timeDiff//60)}:{int(timeDiff%60)}s")
        with open("dungeon_time.txt", "a") as file:
            file.write(f"{int(timeDiff//60)}:{int(timeDiff%60)}\n")
        if timeDiff < 10 * 60:
            pyautogui.sleep(10 * 60 - timeDiff)
            if timeDiff >= 8 * 60 - 10 and timeDiff < 8 * 60 + 10:
                pyautogui.sleep(10)
            print("Done waiting! I'm starting the dungeon again!")