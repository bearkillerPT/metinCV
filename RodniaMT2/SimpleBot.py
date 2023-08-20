import pyautogui
import pydirectinput
import autoit
import keyboard
import cv2 as cv
import numpy as np
import copy
import time
import os

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
healthbarnotempty = False
pickupkeypressed = False
healthbar_located = False
pixelcolor = (0, 0, 0)
class Metin:
    def locateHealthBar():
        res=[]
        toInsert = True
        healthbarlocation = pyautogui.locateAllOnScreen(current_dir + '\\images\\1366_768\\bar_full.png', confidence=0.7, grayscale=True)      
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
        template = cv.imread(current_dir + '\\images\\metin.png',0)
        w, h = template.shape[::-1]
        tries = 0
        while not metinhealthbarlocation:
            metinhealthbarlocation = Metin.locateAndFilterProp(client, metin_health_bar_image, confidence=.7)
            print("Metinhealthbarlocation: " + str(metinhealthbarlocation))
            tries += 1
            if metinhealthbarlocation:
                return True
            if tries > 3:
                return False
            pyautogui.sleep(0.2)
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
        #print('collecting loot')
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
        roi_top_left_x = 200
        roi_top_left_y = 350
        roi_bottom_right_x = 2050
        roi_bottom_right_y = 980
        roi_width = roi_bottom_right_x - roi_top_left_x
        roi_height = roi_bottom_right_y - roi_top_left_y
        cropped_screenshot = screenshot[roi_top_left_y:roi_bottom_right_y, roi_top_left_x:roi_bottom_right_x]
        player_pos =  [roi_bottom_right_x//2 - roi_top_left_x, 
                          (roi_bottom_right_y - roi_top_left_y)//2]
        # Orc valley mask
        #mask = cv.inRange(cropped_screenshot, np.array([0, 0, 0]), np.array([51, 255, 89]))
        
        # desert mask
        mask = cv.inRange(cropped_screenshot, np.array([112,0,0]), np.array([128,154,255]))

        # sohan mountain mask
        #mask = cv.inRange(cropped_screenshot, np.array([111,63,42]), np.array([151,192,158]))

        # land of fire
        #mask = cv.inRange(cropped_screenshot, np.array([118,127,36]), np.array([133,184,81]))

        # spiders
        mask = cv.inRange(cropped_screenshot, np.array([93,101,144]), np.array([115,150,250]))

        pyautogui.sleep(2.5)
        # Step 5: Find contours or location of the object
        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        if contours:
            # find the closes contour to the center of the image and contour are > 1500
            selected_contour = None
            selected_contour_distance_to_center = 0
            monster_mask = cv.inRange(cropped_screenshot, np.array([57, 0, 10]), np.array([179, 148, 200]))
            monster_detection_box_size = 0
            for contour in contours:
                print(cv.contourArea(contour))
                if cv.contourArea(contour) > 300: #900
                    # Metin and monsters mask
                    x, y, w, h = cv.boundingRect(contour)
                    w += monster_detection_box_size
                    h += monster_detection_box_size
                    # check if in monster mask there is a monster near the metin position
                    monster_mask_roi = monster_mask[y-monster_detection_box_size:y+h+monster_detection_box_size, x-monster_detection_box_size:x+w+monster_detection_box_size]
                    # if the amount of white pixels is more than 10% of the area, then there is a monster
                    if cv.countNonZero(monster_mask_roi) > (w*h)*0.7:
                        print("Monster near metin, skipping", cv.countNonZero(monster_mask_roi) ,(w*h))
                        selected_contour = contour
                        break
                    if selected_contour is None:
                        selected_contour = contour
                    else:
                        current_countour_distance_to_center = abs(player_pos[0] - contour[0][0][0]) + abs(player_pos[1] - contour[0][0][1]) 
                        if current_countour_distance_to_center < selected_contour_distance_to_center:
                            selected_contour = contour
            if selected_contour is None:
                return False
            x, y, w, h = cv.boundingRect(selected_contour)
            object_center_x = x + w // 2
            object_center_y = y + h // 2
            # Step 6: Click on the detected object
            pyautogui.moveTo(roi_top_left_x + object_center_x, roi_top_left_y + object_center_y, 0.2)
            autoit.mouse_click("left", roi_top_left_x + object_center_x, roi_top_left_y + object_center_y, 2)
            # write the masked image to disk with a rect drawn around the detected object
            print("Metin found! (",roi_top_left_x + object_center_x, ", ", roi_top_left_y + object_center_y, ") and area: ", cv.contourArea(selected_contour))
            
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
            cv.imwrite("monstermask.png", monster_mask)
            
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
            pydirectinput.press('2')

            
            
    
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
        print("Healthbarposition located: " + str(location))
        break
    while True:
        # check if then End key is pressed
        if keyboard.is_pressed('end'):
            break
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
        #pyautogui.moveTo(client["window_top"][0], client["window_top"][1], 0.2)
        #autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2, 1)
        if Metin.locateAndFilterProp(client, settings_image):
                print("Closing Settings!")
                pydirectinput.press('escape')
        #try to find a metin:
        if len(Metin.locateAllAndFilterProp(client, lvl)) > 1:
            pydirectinput.keyDown('a')
            pydirectinput.keyDown('s')
            pyautogui.sleep(2)
            pydirectinput.keyUp('a')
            pydirectinput.keyUp('s')
            print("More than one lvl indicator found")
            continue
        if not client["farming"]:
            client["not_farming_loop_counter"] += 1
            if(Metin.locateAndFilterProp(client, metin_health_bar_image)):
                print("Metin is being targeted for too long!")
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
                continue
            if Metin.findMetinOpenCV(client):
                client["bugged_timer"] = time.time()
                client["farming"] = True
                pyautogui.sleep(1)
                continue
            else:
                Metin.lookaround()
                Metin.lookaround()
                continue
            #check if the metin is still alive
        if Metin.checkIfMetinStillAlive(client):
            if(time.time() - client["bugged_timer"] > 5):
                Metin.collectLoot(client)
                pydirectinput.keyDown('a')
                pydirectinput.keyDown('s')
                #pydirectinput.keyDown('q')
                pyautogui.sleep(1)
                pydirectinput.keyUp('a')
                pydirectinput.keyUp('s')
                #pydirectinput.keyUp('q')
                client["bugged_timer"] = time.time()
                client["farming"] = True
                #print("UnBugging client " + str(client["client_id"]) + "!")
        else:
            client["farming"] = False
            Metin.collectLoot(client)
            if Metin.findMetinOpenCV(client):
                client["bugged_timer"] = time.time()
                client["farming"] = True
                client["not_farming_loop_counter"] = 0

                















if __name__ == '__main__':
    #Metin.farm()
<<<<<<< HEAD

    import pyautogui
    import pygetwindow as gw
    import time

    from PIL import Image, ImageDraw, ImageOps

    ############# DETECT SCREEN ###################

    # Wait for a few seconds to give you time to focus on the application's window
    time.sleep(5)



   

    # Specify the title of the application's window
    app_window_title = "Rodnia - The King's Return"
    template_image_path = "metin.png"  # Path to the template image

    # Find the application window by its title
    app_window = gw.getWindowsWithTitle(app_window_title)
    if app_window:
        window = app_window[0]
        
        # Get the window's coordinates and dimensions
        left, top, width, height = window.left, window.top, window.width, window.height

        button_x = left + (app_window[0].width // 2)
        button_y = top + (app_window[0].height // 2)

        # Move the mouse to the button's location and click
        print("Moving and clicking....")
        pyautogui.moveTo(button_x, button_y)
        pyautogui.click()

        while True:
            # Capture a screenshot of the window
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            screenshot.save('screenshot.png')

            screenshot_cv_color = cv.cvtColor(np.array(screenshot), cv.COLOR_RGB2HSV)


            mask = cv.inRange(screenshot_cv_color, np.array([93,101,144]), np.array([115,150,250]))

            
            cv.imwrite('screenshot.png', screenshot_cv_color)

            
            # Load the larger image (haystack) and the image to locate (needle)
            haystack_path = 'screenshot.png'
            needle_path = 'metin1.png'

            haystack_image = Image.open(haystack_path)
            needle_image = Image.open(needle_path)

            # Find the location of the metin in the game screen
            location = pyautogui.locate(needle_image, haystack_image, grayscale=True, confidence=0.6)

            if location:
                print(location)

                img_with_box = screenshot.copy()
                draw = ImageDraw.Draw(img_with_box)
                draw.rectangle([location.left, location.top, location.left + location.width, location.top + location.height], outline="red", width=2)

                # Save the image with the box
                img_with_box.save("screenshot_with_box.png")
            else:
                print("Metin not found")

            time.sleep(1)
            
            
    else:
        print("Application window not found.")


    ################## CLICK ON METINS ################

    # Optional: You can add some delay to give the app time to respond
    time.sleep(2)

    # Close the app or perform other actions if needed
    # ...




    # Move the mouse back to a safe location
    pyautogui.moveTo(0, 0)



    



    # run_bot()
=======
    #run_bot()
    while True:
        fishingWindow_image_loc = pyautogui.locateAllOnScreen(fishingWindow_image, confidence=0.6, grayscale=True)
        for i, fishingWindow in enumerate(fishingWindow_image_loc):
           print(i, "Fishing Window found! " + str(fishingWindow))
        pyautogui.sleep(.2)
>>>>>>> 7f6563c22c5a441593b9edefbd4bf55fffeb3610
