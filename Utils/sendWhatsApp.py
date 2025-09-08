import pyautogui, pyperclip, time

INPUT_X = 655
INPUT_Y = 730

def send_whatsapp_message(message):
    pyautogui.click(INPUT_X, INPUT_Y)
    time.sleep(0.5)

    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")

    time.sleep(0.5)
    pyautogui.press("enter")
