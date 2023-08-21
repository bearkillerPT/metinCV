import pygetwindow as gw
import pyautogui

# Replace "Window Title" with the title of the target window
window = gw.getWindowsWithTitle('Rodnia - The King\'s Return')[0]

# Get window position and size
window_position = (window.left, window.top)
window_size = (window.width, window.height)

# Capture a screenshot of the window
screenshot = pyautogui.screenshot(region=window_position + window_size)

# Save the screenshot
screenshot.save("window_screenshot.png")
