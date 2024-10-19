import pyautogui
import pydirectinput
import time
from beranSetao import completeDungeon as completeBeranSetao
from devilTower import completeDungeon as completeDevilTower
from utils import getFormattedTime
from functionTimer import call_with_timeout

beran_setao_time = 0
beran_setao_timeout = 60 * 60 #1 hour
devil_tower_start_time = 0
devil_tower_timeout = 10 * 60 #10 minutes

enabled_dungeons = {
    "beranSetao": False,
    "devilTower": True
}

if __name__ == "__main__":
    while True:
        if enabled_dungeons["beranSetao"]:
            if time.time() - beran_setao_time > beran_setao_timeout:
                beran_setao_time = time.time()
                completeBeranSetao()
                print("Finished in ", getFormattedTime(time.time() - beran_setao_time))
        if enabled_dungeons["devilTower"]:
            if time.time() - devil_tower_start_time > devil_tower_timeout:
                devil_tower_start_time = time.time()                 
                try:
                    timeDiff = completeDevilTower()
                    
                    max_time_offset = 10
                    # print formatted time
                    print("Started at:", time.strftime('%H:%M:%S', time.localtime(devil_tower_start_time)))
                    print("Finished in ", getFormattedTime(timeDiff))
                    print('Ended at:', time.strftime('%H:%M:%S', time.localtime(time.time())))
                    if timeDiff < devil_tower_timeout:
                        print("Waiting for the cooldown to end... Starting again at:", time.strftime('%H:%M:%S', time.localtime(time.time() + devil_tower_timeout - timeDiff)))
                        pyautogui.sleep(devil_tower_timeout - timeDiff)
                            
                        if timeDiff >= 8 * 60 - max_time_offset and timeDiff < 8 * 60 + max_time_offset:
                            pyautogui.sleep(max_time_offset)
                    print("Done waiting! I'm starting the dungeon again!")
                except Exception as e:
                    print(e)