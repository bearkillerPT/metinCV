import os
import pyautogui
import cv2
import easyocr
import numpy as np
from random import randint

reader = easyocr.Reader(['en'], gpu=True)

cwd = os.path.dirname(os.path.abspath(__file__))
captcha_header_filename = os.path.join(cwd, "images\\captcha.png")

homoglyphs = {
    'A': ['4'],
    'B': ['8'],
    'E': ['3'],
    'G': ['6'],
    'I': ['1', 'l', 'L'],
    'L': ['1', 'l', 'I'],
    'O': ['0'],
    'S': ['5', 's'],
    'Z': ['2'],
    'Y': ['V'],
    'U': ['u'],
    'V': ['Y'],
    'a': ['%'],
    'b': ['6'],
    'g': ['9'],
    'i': ['1', 'l'],
    'l': ['1', 'I'],
    'o': ['0'],
    's': ['5', 'S'],
    'u': ['U'],
    'z': ['2'],
    '0': ['O', 'o'],
    '1': ['I', 'l'],
    '2': ['Z', 'z'],
    '3': ['E'],
    '4': ['A'],
    '5': ['S', 's'],
    '6': ['b'],
    '8': ['B'],
    '9': ['g'],
    '%': ['a']
}

two_char_homoglyphs = {
    'a': ['ci'],
    'd': ['cl'],
    'g': ['cj'],
    'm': ['rn'],
    'u': ['ll'],
    'A': ['fi'],
    'W': ['VV'],
    'U': ['ll'],
}

class CaptchaSolver:
    def character_similarity(c1, c2):
        c1_upper = c1.upper()
        c2_upper = c2.upper()
        if c1_upper and c2_upper and c1_upper == c2_upper:
            return 1
        if c1 in homoglyphs and c2 in homoglyphs[c1] or c2 in homoglyphs and c1 in homoglyphs[c2] or c1 in two_char_homoglyphs and c2 in two_char_homoglyphs[c1] or c2 in two_char_homoglyphs and c1 in two_char_homoglyphs[c2]:
            return 0.5
        return 0

    def sanitize_text(text):
        return ''.join([c for c in text if c.isalnum()])

    def text_similarity(prediction, real_text):
        sanitized_prediction = CaptchaSolver.sanitize_text(prediction)
        saintized_real_text = CaptchaSolver.sanitize_text(real_text)
        print("Sanitized Prediction: ", sanitized_prediction, "Sanitized Real Text: ", saintized_real_text)
        if len(sanitized_prediction) != len(saintized_real_text):
            if len(sanitized_prediction) == 1 and sanitized_prediction in two_char_homoglyphs:
                min_len = min(len(two_char_homoglyphs[sanitized_prediction]), len(saintized_real_text))
                return sum([CaptchaSolver.character_similarity(two_char_homoglyphs[sanitized_prediction][i], saintized_real_text[i]) for i in range(min_len)])/min_len
        else:
            return sum([CaptchaSolver.character_similarity(sanitized_prediction[i], saintized_real_text[i]) for i in range(len(sanitized_prediction))])/len(sanitized_prediction)

    def calculateCaptchaGrid(screenshot):
        header_location = pyautogui.locate(captcha_header_filename, screenshot, confidence=0.7)
        
        if header_location is None:
            print("Header not found")
            return

        header_x, header_y = header_location[0], header_location[1]
        header_width, header_height = header_location[2], header_location[3]
        # based on the header location and size, we can calculate the grid size
        grid_x = int(header_x + header_width * 0.025)
        grid_y = int(header_y + header_height * 1.1)
        grid_width = int(header_width*.95)
        grid_height = int(header_height * 7.5)
        
        return grid_x, grid_y, grid_width, grid_height


    def parseIndividualCaptcha(screenshot):
        grid_x, grid_y, grid_width, grid_height = CaptchaSolver.calculateCaptchaGrid(screenshot)
        
        individual_captchas = []
        
        # crop the multiple images from the 3x2 grid
        for i in range(3):
            for j in range(2):
                captcha_dimensions = (grid_y + int(grid_height/2 * j), grid_y + int(grid_height/2 * (j+1)), grid_x + int(grid_width/3 * i), grid_x + int(grid_width/3 * (i+1)))
                captcha = screenshot[captcha_dimensions[0]:captcha_dimensions[1], captcha_dimensions[2]:captcha_dimensions[3]]
                individual_captchas.append({"img": captcha, "dimensions": captcha_dimensions})
                
        return individual_captchas

    def getRealText(img):
        grid_x, grid_y, grid_width, grid_height = CaptchaSolver.calculateCaptchaGrid(img)
        text_x = grid_x + int(grid_width * .05)
        text_y = grid_y + grid_height + 10
        text_width = grid_width 
        text_height = int(grid_height * 0.25)
        # convert to hsv
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)[text_y:text_y+text_height, text_x:text_x+text_width] 

        # read the text
        text = reader.readtext(img)
        if not text:
            print("No text detected")
            return
        text = text[0][1]
        text = text.split("pictures")[1]
        # if the first char is a space, remove it
        if len(text) > 0 and text[0] == " ":
            text = text[1:]
        text = text.split(" ")[0]
        return text
    
    
    def preprocess_image(img):
        new_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # set the most common color to black
        colors, count = np.unique(new_img, return_counts=True)
        most_common_color = colors[np.argmax(count)]
        new_img[new_img == most_common_color] = 0
        return new_img
    
    def solve(screenshot):
        screenshot = np.array(screenshot)
        individual_captchas = CaptchaSolver.parseIndividualCaptcha(screenshot)
        real_text = CaptchaSolver.getRealText(screenshot)
        best_prediction, pred_location, score = "", (-1,-1,-1,-1), 0
        if not real_text:
            print("No text detected...")
        for captcha in individual_captchas:
            prediction = reader.readtext(CaptchaSolver.preprocess_image(captcha['img']))
            if not prediction:
                print("No text detected")
                continue
            prediction = prediction[0][1]
            similarity = CaptchaSolver.text_similarity(prediction, real_text)
            if not similarity:
                similarity = 0
            print(f"Prediction: {prediction}, Real Text: {real_text}, Similarity: {similarity}")
            if similarity > score:
                best_prediction = prediction
                pred_location = captcha['dimensions']
                score = similarity
        if score == 0:
            print("No good prediction found! Choosing a random one")
            random_index = randint(0, len(individual_captchas)-1)
            best_prediction = reader.readtext(individual_captchas[random_index]['img'])[0][1]
            pred_location = individual_captchas[random_index]['dimensions']
        
        screenshot = np.array(pyautogui.screenshot())
        # draw the box around the prediction
        cv2.rectangle(screenshot, (pred_location[2], pred_location[0]), (pred_location[3], pred_location[1]), (0, 255, 0), 2)
        # convert to RGB, search the SolvedCaptchas folder for i.png and save the image as the next number
        if not os.path.exists(f"{cwd}\\images\\SolvedCaptchas"):
            os.makedirs(f"{cwd}\\images\\SolvedCaptchas")
        i = 1
        while os.path.exists(f"{cwd}\\images\\SolvedCaptchas\\{i}.png"):
            i += 1
        print(f"Prediction: {best_prediction}, Real Text: {real_text}, Score: {score}")
        # write the text on the image
        cv2.putText(screenshot, f"Prediction: {best_prediction}, Real Text: {real_text}, Score: {score}", (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.imwrite(f"{cwd}\\images\\SolvedCaptchas\\{i}.png", screenshot)
        
        return (best_prediction, pred_location), real_text, score
        
captcha_pngs = [f for f in os.listdir(f"{cwd}\\images\\CAPTCHAS") if f.endswith(".png")]
    
if __name__ == "__main__":
    for captcha_png in captcha_pngs:
        screenshot = cv2.imread(f"{cwd}\\images\\CAPTCHAS\\{captcha_png}")
        prediction, real_text, score = CaptchaSolver.solve(screenshot)
        print(f"Prediction: {prediction}, Real Text: {real_text}, Score: {score}")