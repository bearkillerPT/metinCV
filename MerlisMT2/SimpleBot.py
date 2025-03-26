import winsound
import pyautogui
import pydirectinput
import autoit
import keyboard
import cv2 as cv
import numpy as np
import time
import os
import sys
import traceback
import pygetwindow as gw
from CaptchaSolver import CaptchaSolver
from random import randint

# print current dir
current_dir = os.getcwd() 
print(current_dir)

METINTEXTDISTANCE = 60
deliver_button_size = 10
market_button_size = 10
orc_tooth_button_size = 10
submit_button_size = 10
trash_size = 30
metin_health_bar_image = current_dir + '\\images\\metin_hp.png'
lvl = current_dir + '\\images\\lvl.png'
settings_image = current_dir + '\\images\\settings.png'
fishingWindow_image = current_dir + '\\images\\fishingWindow.png'
biologist_deliver = current_dir + '\\images\\biologist\\deliver.png'
biologist_submit = current_dir + '\\images\\biologist\\submit.png'
captcha = current_dir + '\\images\\captcha.png'
healthbarnotempty = False
pickupkeypressed = False
healthbar_located = False
pixelcolor = (0, 0, 0)

start_time = time.time()
last_captcha_time = 0
with open("captcha_logs.txt", "r") as file:
    lines = file.readlines()
    for line in reversed(lines):
        if "Captcha detected at: " in line:
            last_captcha_time = time.mktime(time.strptime(line.split("Captcha detected at: ")[1].split("\n")[0], "%d/%m/%Y %H:%M:%S"))
            break
            
class Metin:
    def locateHealthBar(screenshot):
        res=[]
        toInsert = True
        healthbarlocation = pyautogui.locateAll(current_dir + '\\images\\bar_full.png', screenshot, confidence=0.7, grayscale=True)            
        if healthbarlocation:
            for barlocation in healthbarlocation:
                if len(res) == 0:
                    res.append(barlocation)
                else:
                    for barlocation2 in res:   
                            if abs(barlocation.left - barlocation2.left) < 10:
                                toInsert = False
                    if toInsert:
                        res.append(barlocation)
                    else:
                        toInsert = True            
            return res

    def handleLogout(clients, client):
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] +200, 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1]+200, 2)
        pydirectinput.press('f' + str(clients.index(client) + 2))
        time.sleep(3)
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        pyautogui.press('enter')
        pyautogui.press('enter')
        pyautogui.keyDown('f')
        pyautogui.sleep(2)
        pyautogui.keyUp('f')

    def locateAllAndFilterProp(client, screenshot, prop_image):
        res = []
        prop_locations = pyautogui.locateAll(prop_image, screenshot, confidence=0.8, grayscale=True)
        for prop_location in prop_locations:
            if prop_location[0] > client["healthbar"][0] and prop_location[0] < client["healthbar"][0] + client["healthbar"][2] and prop_location[1] < client["healthbar"][1] and prop_location[1] > client["healthbar"][1]:
                    res.append(prop_location)
        return res

    def locateAndFilterProp(client, screenshot, prop_image, confidence=0.8):
        prop_locations = pyautogui.locateAll(prop_image, screenshot, confidence=confidence)
        try: 
            for prop_location in prop_locations:
                return prop_location
        except Exception as e:
            return None        

    def checkIfMetinStillAlive(client, screenshot):
        template = cv.imread(current_dir + '\\images\\metin.png',0)
        metinhealthbarlocation = Metin.locateAndFilterProp(client, screenshot, metin_health_bar_image, confidence=.65)
        if metinhealthbarlocation:
            return True
        print("Could not find the metin healthbar so I'm trying to find a new metin! If you're attacking a metin please check the metin_health_bar_image image!")
        return False

    def collectLoot(client):
        #print('collecting loot')
        #pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        #autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        pydirectinput.press('z') #cause of us layout


    def findMetinOpenCV(client, screenshot):
        metinhealthbarlocation = Metin.locateAndFilterProp(client, screenshot, metin_health_bar_image)
        if metinhealthbarlocation:
            print("Bugged! Trying again!")
            pyautogui.keyDown('esc')
            pyautogui.keyUp('esc')
            #pyautogui.keyDown('a')
            #pyautogui.keyDown('s')
            #pyautogui.sleep(2)
            #pyautogui.keyUp('a')
            #pyautogui.keyUp('s')
            return False
        hsv_screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_BGR2HSV)
        roi_top_left_x = client["healthbar"][0] 
        roi_top_left_y =   client["healthbar"][1] 
        roi_bottom_right_x = client["healthbar"][2] - 200
        roi_bottom_right_y =    client["healthbar"][3]
        cropped_screenshot = hsv_screenshot[roi_top_left_y:roi_bottom_right_y, roi_top_left_x:roi_bottom_right_x]
        player_pos =  [(roi_bottom_right_x+200)//2 - roi_top_left_x, 
                          (roi_bottom_right_y - roi_top_left_y)//2]
        # Orc valley mask
        #mask = cv.inRange(cropped_screenshot, np.array([0, 0, 0]), np.array([51, 255, 89]))
        
        # desert mask
        # mask = cv.inRange(cropped_screenshot, np.array([112,0,0]), np.array([128,154,255]))
        # desert thoughness mask
        #mask = cv.inRange(cropped_screenshot, np.array([118,59,65]), np.array([130,144,174]))

        # sohan mountain mask
        #mask = cv.inRange(cropped_screenshot, np.array([110, 40, 103]), np.array([128, 255, 255]))

        # land of fire
        #mask = cv.inRange(cropped_screenshot, np.array([123, 0, 0]), np.array([178, 178, 63]))

        # spiders
        #mask = cv.inRange(cropped_screenshot, np.array([93,101,144]), np.array([115,150,250]))

        # papers
        #mask = cv.inRange(cropped_screenshot, np.array([121, 0, 0]), np.array([131, 255, 77]))
        
        # Ghost forest 
        # lvl 75
        #mask = cv.inRange(cropped_screenshot, np.array([103, 75, 28]), np.array([110, 255, 130]))
        # lvl 80
        #mask = cv.inRange(cropped_screenshot, np.array([115, 106, 17]), np.array([179, 215, 134]))

        # Red Forest
        mask = cv.inRange(cropped_screenshot, np.array([109, 138, 134]), np.array([117, 249, 255]))

        # Thunder mountains - Metin of wrath
        #mask = cv.inRange(cropped_screenshot, np.array([0, 10, 12]), np.array([94, 68, 56]))

        # Enchanted forest
        #mask = cv.inRange(cropped_screenshot, np.array([47, 193, 0]), np.array([91, 237, 80]))

        # Zhung Temple
        #mask =  cv.inRange(cropped_screenshot, np.array([109, 138, 134]), np.array([117, 249, 255]))

        # Step 5: Find contours or location of the object
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if contours:
            # find the closes contour to the center of the image and contour are > 1500
            selected_contour = None
            selected_contour_distance_to_center = 10000
            monster_detection_box_size = 0
            for contour in contours:
                area = cv.contourArea(contour)
                if area > 300 and area < 10000: #900
                    # Metin and monsters mask
                    x, y, w, h = cv.boundingRect(contour)
                    w += monster_detection_box_size
                    h += monster_detection_box_size
                    
                    current_countour_distance_to_center = abs(player_pos[0] - contour[0][0][0]) + abs(player_pos[1] - contour[0][0][1]) 
                    if current_countour_distance_to_center < 200:
                        continue
                    if selected_contour is None:
                        selected_contour_distance_to_center = abs(player_pos[0] - contour[0][0][0]) + abs(player_pos[1] - contour[0][0][1])
                        selected_contour = contour
                    elif current_countour_distance_to_center < selected_contour_distance_to_center:
                        selected_contour_distance_to_center = current_countour_distance_to_center
                        selected_contour = contour
            if selected_contour is None:
                print(f"The max area found was {max([cv.contourArea(contour) for contour in contours])}")
                return False
            x, y, w, h = cv.boundingRect(selected_contour)
            object_center_x = x + w // 2
            object_center_y = y + h // 2
            # Step 6: Click on the detected object
            pyautogui.moveTo(roi_top_left_x + object_center_x, roi_top_left_y + object_center_y, .2)
            autoit.mouse_click("left", roi_top_left_x + object_center_x, roi_top_left_y + object_center_y, 2)
            # write the masked image to disk with a rect drawn around the detected object
            print("Metin found! (" + str(roi_top_left_x + object_center_x) + ", " + str(roi_top_left_y + object_center_y) + "), distance to player:", selected_contour_distance_to_center,"and area: ", cv.contourArea(selected_contour))
            
            # draw player_pos
            cv.circle(cropped_screenshot, (roi_bottom_right_x//2 - roi_top_left_x, (roi_bottom_right_y - roi_top_left_y)//2), 25, (0, 0, 0), -1)
            
            cv.rectangle(cropped_screenshot, 
                         (roi_bottom_right_x//2 - roi_top_left_x - monster_detection_box_size, 
                          (roi_bottom_right_y - roi_top_left_y)//2 - monster_detection_box_size), 
                          (roi_bottom_right_x//2 - roi_top_left_x +  monster_detection_box_size,
                            (roi_bottom_right_y - roi_top_left_y)//2 +  monster_detection_box_size),
                         (0, 0, 0), 2)
            cv.rectangle(cropped_screenshot, (x, y), (x + w, y + h), (255, 255, 255), 2,)
            cv.rectangle(cropped_screenshot, (x - monster_detection_box_size, y - monster_detection_box_size), (x + w + monster_detection_box_size, y + h + monster_detection_box_size), (255, 0, 0), 2)
            cv.imwrite("res.png", cv.cvtColor(cropped_screenshot, cv.COLOR_HSV2RGB))
            cv.imwrite("mask.png", mask)
            return True
        else:
            print("Object not found.")
            return False


        
    def lookaround():
        print('looking around')
        pydirectinput.keyDown('q')
        pyautogui.sleep(.75)
        pydirectinput.keyUp('q')

    def useSkills(client):
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

    def biologist(client):
        print("biologist!")
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        biologist_deliver_location = Metin.locateAndFilterProp(client, pyautogui.screenshot(), biologist_deliver)
        if(biologist_deliver_location):
            pyautogui.moveTo(int((biologist_deliver_location[0] + biologist_deliver_location[0] + deliver_button_size)/2) , int((biologist_deliver_location[1] + biologist_deliver_location[1] + deliver_button_size)/2) , 0.1)
            autoit.mouse_click("left",int((biologist_deliver_location[0] + biologist_deliver_location[0] + deliver_button_size)/2), int((biologist_deliver_location[1] + biologist_deliver_location[1] + deliver_button_size)/2), 1)
            while (biologist_submit_location:=Metin.locateAndFilterProp(client, pyautogui.screenshot(), biologist_submit, confidence=0.8)) is None:
                pyautogui.sleep(0.1)
                print("waiting for submit button")
            pyautogui.moveTo(int((biologist_submit_location[0] + biologist_submit_location[0] + submit_button_size)/2) , int((biologist_submit_location[1] + biologist_submit_location[1] + submit_button_size)/2) , 0.1)
            autoit.mouse_click("left",int((biologist_submit_location[0] + biologist_submit_location[0] + submit_button_size)/2), int((biologist_submit_location[1] + biologist_submit_location[1] + submit_button_size)/2), 1)
        pyautogui.sleep(.1)
        pydirectinput.press('escape')

    def clearInventory(client):
        deleted = []
        print("Cleaning Inventory!")
        pydirectinput.press('i')
        trash_items = [trash_1, trash_2, trash_3]
        for trash_item in trash_items:
            trash = Metin.locateAndFilterProp(client, trash_item)
            while trash and not deleted.__contains__(trash) and time.time() - client["clear_inventory_bugged_timer"] < 50: 
                pyautogui.moveTo(int((trash[0] + trash[0] + trash_size)/2) , int((trash[1] + trash[1] + trash_size)/2) , 0.1)
                autoit.mouse_click("left",int((trash[0] + trash[0] + trash_size)/2), int((trash[1] + trash[1] + trash_size)/2), 1)
                pyautogui.moveTo(client["window_top"][0] + 150, client["window_top"][1] + 150, 0.1)
                autoit.mouse_click("left",client["window_top"][0] + 150, client["window_top"][1] + 150, 1)
                pyautogui.sleep(0.1)
                submit = Metin.locateAndFilterProp(client, destroy_item)
                if submit:
                    print("Item Deleted!")
                    destroy_button = int(submit[0] + 3* submit[2]/4 + 20), int(submit[1] + submit[3]/2)
                    pyautogui.moveTo(destroy_button[0], destroy_button[1] , 0.2)
                    autoit.mouse_click("left", destroy_button[0], destroy_button[1], 1)
                    pyautogui.sleep(0.4)
                    deleted.append(trash)
                    trash = Metin.locateAndFilterProp(client, trash_item)
        pydirectinput.press('i')
        
    def farm(client):
        pydirectinput.keyDown("space")
        while True:
            pydirectinput.keyDown("space")
            screenshot = pyautogui.screenshot()
            if keyboard.is_pressed('end'):
                print('Bot paused!')
                pyautogui.sleep(2)
                while not keyboard.is_pressed('end'):
                    pyautogui.sleep(.25)
                print('Bot resumed!')
            if Metin.locateAndFilterProp(client, screenshot, captcha):
                # dd/mm/YY HH:MM:SS
                print("OH jees, captcha!")
                
                duration = 1000  # milliseconds
                freq = 440  # Hz
                winsound.Beep(freq, duration)
                
                (_, captcha_box), _, _ = CaptchaSolver.solve(screenshot)
                # move to the center of the captcha box
                pyautogui.moveTo(captcha_box[2] + (captcha_box[3] - captcha_box[2])//2, captcha_box[0] + (captcha_box[1] - captcha_box[0])//2)
                pyautogui.sleep(.1)
                pyautogui.click()

                i = 1
                while os.path.exists(current_dir + "\\images\\CAPTCHAS\\" + str(i) + ".png"):
                    i += 1
                screenshot.save(current_dir + "\\images\\CAPTCHAS\\" + str(i) + ".png")
            
            pydirectinput.press('2')
            pyautogui.sleep(2)
            pydirectinput.press('z')
            pyautogui.sleep(2)

            
client_box = [0,0,0,0]    
    
def run_bot():
    global client_box
    global start_time
    global last_captcha_time
    # Locate the Healthbar for init
    client_box = gw.getWindowsWithTitle('Merlis')[0]
    print(client_box)
    
    client = {"client_id" : 0,
            "healthbar": [
                client_box.left + 200 * client_box.width // 2073,
                client_box.top + 300 * client_box.height // 1211,
                client_box.width - 25 * client_box.width // 2073,
                client_box.height - 125 * client_box.height // 1211
            ],
            "skills_timer" : 0,
            "bugged_timer": 0,
            "biologist_timer": 0,
            "clear_inventory_timer" : 0,
            "clear_inventory_bugged_timer" : 0,
            "not_farming_loop_counter": 0,
            "farming": False,
            "window_top": (client_box.left, client_box.top)
    }

    with open("captcha_logs.txt", "a") as file:
        file.write("Starting to farm at: " + time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
    
    print("Starting to farm!")
    #Metin.farm(client)
    
    while True:
        # Check if the game is the active window
        currently_active_window = gw.getActiveWindow()
        if not currently_active_window or not client_box or currently_active_window._hWnd != client_box._hWnd:
            print("Merlis is not the active window!", end="\r")
            pyautogui.sleep(1)
            continue
        
        # check if then End key is pressed
        if keyboard.is_pressed('end'):
            print('Bot paused!')
            with open("captcha_logs.txt", "a") as file:
                file.write("Bot paused at: " + time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
                pyautogui.sleep(2)
                while True:
                    if keyboard.is_pressed('end'):
                        print('Bot resumed!')
                        file.write("Bot resumed at: " + time.strftime("%d/%m/%Y %H:%M:%S") + "\n")
                        break
                    pyautogui.sleep(.5)
        # use skills
        if time.time() - client["skills_timer"] > 60 * 5:
            Metin.useSkills(client)
            client["skills_timer"] = time.time()
        # try to deliver an item
        if time.time() - client["biologist_timer"] > 60 * 60 * 2:
            Metin.biologist(client)
            client["biologist_timer"] = time.time()
                    
        screenshot = pyautogui.screenshot()
                    
        if not client["farming"]:
            if Metin.locateAndFilterProp(client, screenshot, settings_image):
                print("Closing Settings!")
                pydirectinput.press('escape')
            client["not_farming_loop_counter"] += 1
            if(Metin.locateAndFilterProp(client, screenshot, metin_health_bar_image)):
                #print("Metin is being targeted for too long!")
                #Metin.collectLoot(client)
                #pydirectinput.keyDown('space')
                #pyautogui.sleep(1)
                #pydirectinput.keyUp('space')
                #pydirectinput.keyDown('a')
                #pydirectinput.keyDown('s')
                #pyautogui.sleep(1)
                #pydirectinput.keyUp('a')
                #pydirectinput.keyUp('s')
                #pydirectinput.press('escape')
                #zclient["bugged_timer"] = time.time()
                continue
            if Metin.findMetinOpenCV(client,  screenshot):
                farming_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                time_since_last_captcha = time.strftime("%H:%M:%S", time.gmtime(time.time() - last_captcha_time if last_captcha_time != 0 else 0))
                print("Farming at: " + farming_time + " and last captcha was: " + time_since_last_captcha + " ago!")
                client["bugged_timer"] = time.time()
                client["farming"] = True
                pyautogui.sleep(1)
                continue
            else:
                Metin.lookaround()
                continue
        else:
            # check for captcha
            if Metin.locateAndFilterProp(client, screenshot, captcha):
                # dd/mm/YY HH:MM:SS
                last_captcha_time = time.time()
                formated_current_time = time.strftime("%d/%m/%Y %H:%M:%S", time.gmtime(last_captcha_time))
                with open("captcha_logs.txt", "a") as file:
                    file.write("Captcha detected at: " + formated_current_time + "\n")
                print("OH jees, captcha!")
                
                duration = 1000  # milliseconds
                freq = 440  # Hz
                winsound.Beep(freq, duration)
                
                (_, captcha_box), _, _ = CaptchaSolver.solve(screenshot)
                # move to the center of the captcha box
                pyautogui.moveTo(captcha_box[2] + (captcha_box[3] - captcha_box[2])//2, captcha_box[0] + (captcha_box[1] - captcha_box[0])//2)
                pyautogui.sleep(.1)
                pyautogui.click()

                i = 1
                while os.path.exists(current_dir + "\\images\\CAPTCHAS\\" + str(i) + ".png"):
                    i += 1
                screenshot.save(current_dir + "\\images\\CAPTCHAS\\" + str(i) + ".png")
            
            #check if the metin is still alive
            if Metin.checkIfMetinStillAlive(client,  screenshot):
                Metin.collectLoot(client)
                if(time.time() - client["bugged_timer"] > 15):
                    bugged_timer_start_time = time.time()
                    random = randint(0, 1)
                    camera_direction = 'q' if random == 0 else 'e'
                    horizontal_direction = 'a' if random == 0 else 'd'
                    while time.time() - bugged_timer_start_time < 1:
                        Metin.collectLoot(client)
                        pydirectinput.keyDown('s')
                        pydirectinput.keyDown(camera_direction)
                        pydirectinput.keyDown(horizontal_direction)
                        pyautogui.sleep(.1)
                        pydirectinput.keyUp('s')
                        pydirectinput.keyUp(camera_direction)
                        pydirectinput.keyUp(horizontal_direction)
                    client["bugged_timer"] = time.time()
                    client["farming"] = True
                    print("UnBugging client " + str(client["client_id"]) + "!")
            else:
                client["farming"] = False
                Metin.collectLoot(client)
                pyautogui.sleep(.2)
                Metin.collectLoot(client)
                if Metin.findMetinOpenCV(client,  screenshot):
                    farming_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
                    time_since_last_captcha = time.strftime("%H:%M:%S", time.gmtime(time.time() - last_captcha_time if last_captcha_time != 0 else 0))
                    print("Farming at: " + farming_time + " and last captcha was: " + time_since_last_captcha + " ago!")
                    pyautogui.sleep(1)
                    client["bugged_timer"] = time.time()
                    client["farming"] = True
                    client["not_farming_loop_counter"] = 0

                



if __name__ == '__main__':
    pyautogui.FAILSAFE = False
    pydirectinput.FAILSAFE = False
    try:
        run_bot()
    except KeyboardInterrupt:
        print("Ending the bot!")
        with open("captcha_logs.txt", "a") as file:
            file.write("Ending the bot at: " + time.strftime("%d/%m/%Y %H:%M:%S") + "\n\n")
        # print the stack trace
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print("*** print_exception:")
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                                  limit=2, file=sys.stdout)
        exit(0)