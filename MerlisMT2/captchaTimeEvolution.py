import os
import time

CWD = os.path.dirname(os.path.abspath(__file__))
captcha_logs = os.path.join(CWD, "captcha_logs.txt")

captchas_time_offsets = []

with open(captcha_logs, "r") as f:
    lines = f.readlines()
    last_captcha_time = 0
    
    for line in lines:
        if "Captcha detected at: " in line:
            # example:  "18/08/2024 01:52:43"
            captcha_time = line.split("Captcha detected at: ")[1].strip()

            if last_captcha_time == 0:
                last_captcha_time = time.mktime(time.strptime(captcha_time, "%d/%m/%Y %H:%M:%S"))
            else:
                current_captcha_time = time.mktime(time.strptime(captcha_time, "%d/%m/%Y %H:%M:%S"))
                time_offset = current_captcha_time - last_captcha_time
                captchas_time_offsets.append(time_offset)
                last_captcha_time = current_captcha_time
                
                
# sort by least to most time offset and convert to hh:mm:ss
captchas_time_offsets.sort()
captchas_time_offsets = [time.strftime("%H:%M:%S", time.gmtime(time_offset)) for time_offset in captchas_time_offsets]

print(captchas_time_offsets)
                