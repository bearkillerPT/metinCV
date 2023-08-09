from PIL.ImageOps import grayscale
import pyautogui
import pydirectinput
import time
import autoit
import math
import cv2 as cv
import numpy as np
import copy
METINTEXTDISTANCE = 60
deliver_button_size = 10
market_button_size = 10
orc_tooth_button_size = 10
submit_button_size = 10
trash_size = 30
metin_health_bar_image = 'C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\metin_hp.png'
lvl = 'C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\lvl.png'
healthbarnotempty = False
pickupkeypressed = False
healthbar_located = False
pixelcolor = (0, 0, 0)
class Metin:
    def locateHealthBar():
        res=[]
        toInsert = True
        healthbarlocation = pyautogui.locateAllOnScreen('C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\bar_full.png', confidence=0.9)            
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
            for barlocation in res:
                print("Healthbarposition located: " + str(barlocation))
            
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

    def locateAllAndFilterProp(client, prop_image):
        res = []
        prop_locations = pyautogui.locateAllOnScreen(prop_image, confidence=0.8, grayscale=True)
        for prop_location in prop_locations:
            if prop_location[0] > client["healthbar"][0] and prop_location[0] < client["healthbar"][0] + 800 and prop_location[1] < client["healthbar"][1] and prop_location[1] > client["healthbar"][1] - 900:
                    res.append(prop_location)
        return res

    def locateAndFilterProp(client, prop_image, confidence=0.8):
        prop_locations = pyautogui.locateAllOnScreen(prop_image, confidence=confidence)
        for prop_location in prop_locations:
            return prop_location
                

    def checkIfMetinStillAlive(client):
        metinhealthbarlocation = 0
        template = cv.imread('C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\metin.png',0)
        w, h = template.shape[::-1]
        while not metinhealthbarlocation:
            metinhealthbarlocation = Metin.locateAndFilterProp(client, metin_health_bar_image)
            screenshot = np.array(pyautogui.screenshot()) 
            img_gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
            if metinhealthbarlocation:
                return True
                #cv.rectangle(img_gray, (healthbarlocation.left -120, healthbarlocation.top + h -10), (healthbarlocation.left -132, healthbarlocation.top + h), (0,0,255), 2)
                #cv.imwrite('res.png',img_gray)
            return False
        leftouterpixellocation_x = int(metinhealthbarlocation.left -132)
        leftouterpixellocation_y = int(metinhealthbarlocation.top + h -5)
        # Try to get the Pixel-Color
        checkedColor = False
        pixelcolor = (0, 0, 0)
        
        try:
            pixelcolor = pyautogui.pixel(leftouterpixellocation_x, leftouterpixellocation_y)
            checkedColor = True
            print(pixelcolor)
        except Exception:
            print(Exception)
            return True

        if pixelcolor == (249, 108, 109):
            return True

        elif checkedColor:
            print('Pixelcolor: ' + str(pixelcolor))
            return False

    def collectLoot(client):
        print('collecting loot')
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        pydirectinput.press('z') #cause of us layout


    def findMetinOpenCV(client, roi=None):
        metinhealthbarlocation = Metin.locateAndFilterProp(client, metin_health_bar_image)
        if metinhealthbarlocation:
            Metin.collectLoot(client)
            print("Bugged! Trying again!")
            pyautogui.keyDown('esc')
            pyautogui.keyUp('esc')
            pyautogui.keyDown('a')
            pyautogui.keyDown('s')
            pyautogui.sleep(2)
            pyautogui.keyUp('a')
            pyautogui.keyUp('s')
            pyautogui.press('q')
            pyautogui.press('q')
            return False
        screenshot = pyautogui.screenshot()
        screenshot = cv.cvtColor(np.array(screenshot), cv.COLOR_BGR2HSV)
        roi_top_left_x = 0
        roi_top_left_y = 250
        roi_bottom_right_x = 2500
        roi_bottom_right_y = 1100
        cropped_screenshot = screenshot[roi_top_left_y:roi_bottom_right_y, roi_top_left_x:roi_bottom_right_x]

        lower_color = np.array([0, 0, 0])
        upper_color = np.array([51, 255, 89])

        mask = cv.inRange(cropped_screenshot, lower_color, upper_color)
        
        pyautogui.sleep(2.5)
        # Step 5: Find contours or location of the object
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if contours:
            # find the closes contour to the center of the image and contour are > 1500
            selected_contour = None
            for contour in contours:
                if cv.contourArea(contour) > 1500:
                    if selected_contour is None:
                        selected_contour = contour
                    else:
                        current_countour_distance_to_center = math.sqrt((roi_bottom_right_x / 2 - contour[0][0][0]) ** 2 + (roi_bottom_right_y / 2 - contour[0][0][1]) ** 2)
                        selected_contour_distance_to_center = math.sqrt((roi_bottom_right_x / 2 - selected_contour[0][0][0]) ** 2 + (roi_bottom_right_y / 2 - selected_contour[0][0][1]) ** 2)
                        if current_countour_distance_to_center < selected_contour_distance_to_center:
                            selected_contour = contour
            if selected_contour is None:
                return False
            
            # print the area
            print(cv.contourArea(selected_contour))
            x, y, w, h = cv.boundingRect(selected_contour)
            object_center_x = x + w // 2
            object_center_y = y + h // 2
            # Step 6: Click on the detected object
            pyautogui.moveTo(roi_top_left_x + object_center_x, roi_top_left_y + object_center_y - 15, 0.2)
            autoit.mouse_click("left", roi_top_left_x + object_center_x, roi_top_left_y + object_center_y - 15, 2)
            # write the masked image to disk with a rect drawn around the detected object
            print("Object found with area: " + str(cv.contourArea(selected_contour)))
            cv.rectangle(screenshot, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv.imwrite("res.png", cv.cvtColor(screenshot, cv.COLOR_HSV2BGR))
            cv.imwrite("mask.png", mask)
            
            return True
        else:
            print("Object not found.")
            return False


        
    def lookaround():
        print('looking around')
        pydirectinput.press('q')
        pydirectinput.press('q')
        pydirectinput.press('q')
        pydirectinput.press('q')

        #pydirectinput.D('left')
        #pydirectinput.keyUp('left')

    def useSkills(client):
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
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
        biologist_deliver_location = Metin.locateAndFilterProp(client, biologist_deliver)
        if(biologist_deliver_location):
            pyautogui.moveTo(int((biologist_deliver_location[0] + biologist_deliver_location[0] + deliver_button_size)/2) , int((biologist_deliver_location[1] + biologist_deliver_location[1] + deliver_button_size)/2) , 0.2)
            autoit.mouse_click("left",int((biologist_deliver_location[0] + biologist_deliver_location[0] + deliver_button_size)/2), int((biologist_deliver_location[1] + biologist_deliver_location[1] + deliver_button_size)/2), 2)
            biologist_market_location = [0,0,10,10]
            pyautogui.sleep(1)
            biologist_submit_location = Metin.locateAndFilterProp(client, biologist_submit)
            if biologist_submit_location:
                biologist_market_location[0] = biologist_submit_location[0] + biologist_submit_location[2] + 42 
                biologist_market_location[1] = biologist_submit_location[1] + 47
                pyautogui.sleep(1)
                pyautogui.moveTo(int((biologist_market_location[0] + biologist_market_location[0] + market_button_size)/2) , int((biologist_market_location[1] + biologist_market_location[1] + market_button_size)/2) , 0.2)
                autoit.mouse_click("left",int((biologist_market_location[0] + biologist_market_location[0] + market_button_size)/2), int((biologist_market_location[1] + biologist_market_location[1] + market_button_size)/2), 2)
                pydirectinput.press('i')
                pyautogui.sleep(1)
                biologist_orc_tooth_location = Metin.locateAndFilterProp(client, biologist_orc_tooth)
                if biologist_orc_tooth_location:
                    pyautogui.moveTo(int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2) , int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2) , 0.2)
                    autoit.mouse_click("right",int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2), int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2), 2)
                    pydirectinput.press('escape')
                    pyautogui.sleep(2)
                    if biologist_submit_location:
                        pyautogui.moveTo(int((biologist_submit_location[0] + biologist_submit_location[0] + submit_button_size)/2) , int((biologist_submit_location[1] + biologist_submit_location[1] + submit_button_size)/2) , 0.2)
                        autoit.mouse_click("left",int((biologist_submit_location[0] + biologist_submit_location[0] + submit_button_size)/2), int((biologist_submit_location[1] + biologist_submit_location[1] + submit_button_size)/2), 2)
                        client["biologist_timer"] = time.time()
                else:
                    pyautogui.sleep(1)
                    pyautogui.moveTo(client["window_top"][0], client["window_top"][1], 0.2)
                    autoit.mouse_click("left",client["window_top"][0], client["window_top"][1],2)
                    pydirectinput.press('escape')
            pyautogui.sleep(1)
            pyautogui.moveTo(int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2) , int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2) , 0.2)
            autoit.mouse_click("right",int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2), int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2), 2)
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
        
    def farm():
        while True:
            pydirectinput.keyDown("space")
            pyautogui.sleep(4)
            pydirectinput.keyUp("space")
            autoit.mouse_click('right')

            
            
    
def run_bot():
    bilogist = False
    # Locate the Healthbar for init
    healthbarlocations = 0
    while not healthbarlocations:
        healthbarlocations = Metin.locateHealthBar()
    client_id = 0
    client = None
    
    for location in healthbarlocations:
        append_dict = {"client_id" : client_id,
                      "healthbar": location,
                      "skills_timer" : 0,
                      "bugged_timer": 0,
                      "biologist_timer": 0,
                      "clear_inventory_timer" : 0,
                      "clear_inventory_bugged_timer" : 0,
                      "not_farming_loop_counter": 0,
                      "farming": False,
                      "window_top": (location[0] + 10, location[1] - 1300)
                     }
        client = copy.deepcopy(append_dict)
        break
    while True:
        Metin.collectLoot(client)
        #noticed that sometimes it doesn't loot
        if client["not_farming_loop_counter"] > 5:
            Metin.collectLoot(client)
            pydirectinput.keyDown('a')
            pydirectinput.keyDown('s')
            pyautogui.sleep(3)
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('s')
            pydirectinput.press('q')
            pydirectinput.press('q')
            client["not_farming_loop_counter"] = 0
        pyautogui.moveTo(client["window_top"][0], client["window_top"][1], 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2, 1)
        #    print("Closing Settings!")
        #    pydirectinput.press('escape')
        #if(time.time() - client["clear_inventory_timer"] > 500):
        #    client["clear_inventory_bugged_timer"] = time.time()
        #    Metin.clearInventory(client)
        #    client["clear_inventory_timer"] = time.time()
        #try to find a metin:
        if len(Metin.locateAllAndFilterProp(client, lvl)) > 1:
            pydirectinput.keyDown('a')
            pydirectinput.keyDown('s')
            pyautogui.sleep(2)
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('s')
            break
        if not client["farming"]:
            client["not_farming_loop_counter"] += 1
            if(Metin.locateAndFilterProp(client, metin_health_bar_image)):
                Metin.collectLoot(client)
                pydirectinput.keyDown('space')
                pyautogui.sleep(1)
                pydirectinput.keyUp('space')
                pydirectinput.keyDown('a')
                pydirectinput.keyDown('s')
                pyautogui.sleep(1)
                pydirectinput.keyUp('a')
                pydirectinput.keyUp('s')
                pydirectinput.press('escape')
                client["bugged_timer"] = time.time()
                break
            if Metin.findMetinOpenCV(client):
                client["bugged_timer"] = time.time()
                client["farming"] = True
                continue
            else:
                Metin.lookaround()
                Metin.lookaround()
                continue
            #check if the metin is still alive
        if Metin.checkIfMetinStillAlive(client):
            if(time.time() - client["bugged_timer"] > 20):
                Metin.collectLoot(client)
                pydirectinput.press('escape')
                pydirectinput.keyDown('a')
                pydirectinput.keyDown('s')
                pydirectinput.keyDown('q')
                pyautogui.sleep(1)
                pydirectinput.keyUp('a')
                pydirectinput.keyUp('s')
                pydirectinput.keyUp('q')
                pydirectinput.keyDown('space')
                time.sleep(1)
                pydirectinput.keyUp('space')
                client["bugged_timer"] = time.time()
                client["farming"] = False
                print("UnBugging client " + str(client["client_id"]) + "!")
        else:
            client["farming"] = False
            Metin.collectLoot(client)
            if Metin.findMetinOpenCV(client):
                client["bugged_timer"] = time.time()
                client["farming"] = True
                client["not_farming_loop_counter"] = 0

                



if __name__ == '__main__':
    run_bot()

# while True:
#     if not Metin.findMetinOpenCV():
#         time.sleep(3)
#     else:

#         healthbarlocation = pyautogui.locateOnScreen('C:\\Users\\gil-t\\Desktop\\dev\\METINCV\\images\\bar_full.png', confidence=0.9, grayscale=True)

#         if healthbarlocation:
#             print("Healthbarposition located: " + str(healthbarlocation))
#             healthbar_located = True
#             leftouterpixellocation_x = int(healthbarlocation.left + 14)
#             leftouterpixellocation_y = int(healthbarlocation.top + 3)

#         while healthbar_located:
#             #pyautogui.screenshot("testshot.png", region=(healthbarlocation))

#             # Try to get the Pixel-Color
#             try:
#                 pixelcolor = pyautogui.pixel(leftouterpixellocation_x, leftouterpixellocation_y)
#             except:
#                 print("Error")

#             # If the Color is 99,39,39 the Healthbar isnt empty
#             if pixelcolor == (99, 39, 39):
#                 pickupkeypressed = False

#             else:
#                 if not pickupkeypressed :
#                     print("press y")
#                     time.sleep(0.5)
#                     pydirectinput.press('z') #cause of us layout
#                     pickupkeypressed = True

#             time.sleep(1)



        # time.sleep(1)

