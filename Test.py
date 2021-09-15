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
metin_health_bar_image = 'C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\metin_hp.png'
logged_out_image = 'C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\logged_out_right.png'
biologist_deliver = 'C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\biologist\\deliver.png'
biologist_market = 'C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\biologist\\market.png'
biologist_orc_tooth = 'C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\biologist\\orc_tooth.png'
biologist_submit = 'C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\biologist\\submit_text.png'
healthbarnotempty = False
pickupkeypressed = False
healthbar_located = False
clients = []
pixelcolor = (0, 0, 0)
class Metin:

    def locateHealthBar():
        res=[]
        toInsert = True
        healthbarlocation = pyautogui.locateAllOnScreen('C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\bar_full.png', confidence=0.9, grayscale=True)            
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
        print("here")
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        pydirectinput.press('f' + str(clients.index(client) + 2))
        time.sleep(2)
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        pyautogui.press('enter')
        pyautogui.press('enter')
        pyautogui.press('enter')
        time.sleep(2)
        
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        Metin.useSkills(client)
        print("here2")



    def locateAllandFilterProp(client, prop_image, prop_type):
        known_types = ["metin_health_bar" ,"logged_out", "deliver", "market", "orc_tooth", "submit"]
        prop_locations = pyautogui.locateAllOnScreen(prop_image, confidence=0.9, grayscale=True)
        for prop_location in prop_locations:
            print(prop_location)
            if prop_location[0] > client["healthbar"][0] and prop_location[0] < client["healthbar"][0] + 800 and prop_location[1] < client["healthbar"][1] and prop_location[1] > client["healthbar"][1] - 900:
                if known_types.__contains__(prop_type):
                    return prop_location
                

    def checkIfMetinStillAlive(client):
        metinhealthbarlocation = 0
        template = cv.imread('C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\metin_writing.png',0)
        w, h = template.shape[::-1]
        while not metinhealthbarlocation:
            metinhealthbarlocation = Metin.locateAllandFilterProp(client, metin_health_bar_image, "metin_health_bar")
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
        pydirectinput.press('z', 3, interval=0.1) #cause of us layout


    def findMetinOpenCV(client):
        metinhealthbarlocation = Metin.locateAllandFilterProp(client, metin_health_bar_image, "metin_health_bar")
        if metinhealthbarlocation:
            print("Bugged! Trying again!")
            pyautogui.keyDown('esc')
            pyautogui.keyUp('esc')
            pyautogui.keyDown('a')
            pyautogui.keyDown('s')
            pyautogui.sleep(3)
            pyautogui.keyUp('a')
            pyautogui.keyUp('s')
            pyautogui.press('q')
            pyautogui.press('q')
            Metin.collectLoot(client)
            return False
        screenshot = np.array(pyautogui.screenshot())[ client["healthbar"][1] - 730 : client["healthbar"][1] - 10, client["healthbar"][0] - 10 :client["healthbar"][0] + 900]
        img_gray = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
        template = cv.imread('C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\metin_writing.png',0)
        w, h = template.shape[::-1]
        cv.imwrite('res.png',img_gray)
        res = cv.matchTemplate(img_gray,template,cv.TM_CCORR_NORMED)
        threshold = 0.85
        loc = np.where( res >= threshold)
        target_dist = 1000
        target = 0
        for pt in zip(*loc[::-1]):
            if(math.sqrt(abs(300 - pt[0]) + abs(400- pt[1] + h + METINTEXTDISTANCE)) < target_dist and pt[0] + w < 750 and pt[1] + h + METINTEXTDISTANCE < 700):
                target = pt
        if not target:
            return False
        #for pt in zip(*loc[::-1]):
        print(f'Metin found at {target[0] + int(w/2)} and {target[1] + h + METINTEXTDISTANCE}')
        pyautogui.moveTo(target[0] + int(w/2) + client["healthbar"][0] - 10, target[1] + h + METINTEXTDISTANCE + client["healthbar"][1] - 730, 0.2)
            #pyautogui.click(clicks=2, interval=0.1)
        autoit.mouse_click("left",target[0] + int(w/2) + client["healthbar"][0] - 10, target[1] + h + METINTEXTDISTANCE + client["healthbar"][1] - 730,2)
            #cv.rectangle(img_gray, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
            #cv.imwrite('res.png',img_gray)
        return True

        print('No Metin found')
        
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
        pydirectinput.press('h')
        pydirectinput.keyUp('ctrl')
        time.sleep(1)
        pydirectinput.press('3')
        time.sleep(2)
        pydirectinput.press('4')
        time.sleep(2)
        pydirectinput.keyDown('ctrl')
        pydirectinput.press('h')
        pydirectinput.keyUp('ctrl')

    def biologist(client):
        print("biologist!")
        pyautogui.moveTo(client["window_top"][0] , client["window_top"][1] , 0.2)
        autoit.mouse_click("left",client["window_top"][0], client["window_top"][1], 2)
        biologist_deliver_location = Metin.locateAllandFilterProp(client, biologist_deliver, "deliver")
        if(biologist_deliver_location):
            pyautogui.moveTo(int((biologist_deliver_location[0] + biologist_deliver_location[0] + deliver_button_size)/2) , int((biologist_deliver_location[1] + biologist_deliver_location[1] + deliver_button_size)/2) , 0.2)
            autoit.mouse_click("left",int((biologist_deliver_location[0] + biologist_deliver_location[0] + deliver_button_size)/2), int((biologist_deliver_location[1] + biologist_deliver_location[1] + deliver_button_size)/2), 2)
            biologist_market_location = [0,0,10,10]
            pyautogui.sleep(1)
            biologist_submit_location = Metin.locateAllandFilterProp(client, biologist_submit, "submit")
            if biologist_submit_location:
                biologist_market_location[0] = biologist_submit_location[0] + biologist_submit_location[2] + 42 
                biologist_market_location[1] = biologist_submit_location[1] + 47
                pyautogui.sleep(1)
                pyautogui.moveTo(int((biologist_market_location[0] + biologist_market_location[0] + market_button_size)/2) , int((biologist_market_location[1] + biologist_market_location[1] + market_button_size)/2) , 0.2)
                autoit.mouse_click("left",int((biologist_market_location[0] + biologist_market_location[0] + market_button_size)/2), int((biologist_market_location[1] + biologist_market_location[1] + market_button_size)/2), 2)
                pyautogui.sleep(4)
                biologist_orc_tooth_location = Metin.locateAllandFilterProp(client, biologist_orc_tooth, "orc_tooth")
                for x in pyautogui.locateAllOnScreen(biologist_orc_tooth):
                    print(x)
                if biologist_orc_tooth_location:
                    pyautogui.moveTo(int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2) , int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2) , 0.2)
                    autoit.mouse_click("right",int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2), int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2), 2)
                    pydirectinput.press('escape')
                    pyautogui.sleep(2)
                    if biologist_submit_location:
                        pyautogui.moveTo(int((biologist_submit_location[0] + biologist_submit_location[0] + submit_button_size)/2) , int((biologist_submit_location[1] + biologist_submit_location[1] + submit_button_size)/2) , 0.2)
                        autoit.mouse_click("left",int((biologist_submit_location[0] + biologist_submit_location[0] + submit_button_size)/2), int((biologist_submit_location[1] + biologist_submit_location[1] + submit_button_size)/2), 2)
                else:
                    pyautogui.sleep(1)
                    pyautogui.moveTo(client["window_top"][0], client["window_top"][1], 0.2)
                    autoit.mouse_click("left",client["window_top"][0], client["window_top"][1],2)
                    pydirectinput.press('escape')
            pyautogui.sleep(1)
            pyautogui.moveTo(int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2) , int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2) , 0.2)
            autoit.mouse_click("right",int((biologist_orc_tooth_location[0] + biologist_orc_tooth_location[0] + orc_tooth_button_size)/2), int((biologist_orc_tooth_location[1] + biologist_orc_tooth_location[1] + orc_tooth_button_size)/2), 2)
            pydirectinput.press('escape')
            client["biologist_timer"] = time.time()

    
def run_bot():
    bilogist = False
    # Locate the Healthbar for init
    healthbarlocations = 0
    while not healthbarlocations:
        healthbarlocations = Metin.locateHealthBar()
    for location in healthbarlocations:
        append_dict = {"healthbar": location,
                      "skills_timer" : 0,
                      "bugged_timer": 0,
                      "biologist_timer": 0,
                      "farming": False,
                      "window_top": (location[0], location[1] - 740)
                     }
        clients.append(copy.deepcopy(append_dict))
    while True:
        for client in clients:
            if bilogist and (time.time() - client["biologist_timer"] > 650):
                Metin.biologist(client)
            loggout_location = Metin.locateAllandFilterProp(client, logged_out_image, "logged_out")
            if loggout_location:
                Metin.handleLogout(clients, client)
                
                
            pyautogui.moveTo(client["window_top"][0], client["window_top"][1], 0.2)
            autoit.mouse_click("left",client["window_top"][0], client["window_top"][1],2)
            
            if( time.time() - client["skills_timer"] > 300):
                client["skills_timer"] = time.time()
                Metin.useSkills(client)
            #try to find a metin:
            #metinhealthbarlocation = Metin.locateMetinHealthBar()
            
            if not client["farming"]:
                if(Metin.locateAllandFilterProp(client, metin_health_bar_image, "metin_health_bar")):
                    pydirectinput.press('escape')
                if Metin.findMetinOpenCV(client):
                    client["bugged_timer"] = time.time()
                    pydirectinput.keyDown('a')
                    pydirectinput.keyDown('s')
                    pyautogui.sleep(3)
                    pydirectinput.keyUp('a')
                    pydirectinput.keyUp('s')
                    pydirectinput.press('q')
                    pydirectinput.press('q')
                    client["farming"] = True
                    break
                else:
                    Metin.lookaround()
                    Metin.lookaround()
                    break
                #check if the metin is still alive
            if Metin.checkIfMetinStillAlive(client):
                if(time.time() - client["bugged_timer"] > 60):
                    
                    pydirectinput.press('escape')
                    pyautogui.press('d')
                    pyautogui.press('d')
                    print("UnBugging!")
                    client["farming"] = False
                    client["bugged_timer"] = time.time()
                    Metin.collectLoot(client)
                    break
            else:
                client["farming"] = False
                pyautogui.moveTo(client["window_top"][0], client["window_top"][1], 0.2)
                autoit.mouse_click("left",client["window_top"][0], client["window_top"][1],2)
                Metin.collectLoot(client)
                if Metin.findMetinOpenCV(client):
                    client["bugged_timer"] = time.time()
                    client["farming"] = True
                    break



if __name__ == '__main__':
        run_bot()

# while True:
#     if not Metin.findMetinOpenCV():
#         time.sleep(3)
#     else:

#         healthbarlocation = pyautogui.locateOnScreen('C:\\Users\\gil-t\\Downloads\\MetinBot-main\\images\\bar_full.png', confidence=0.9, grayscale=True)

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

