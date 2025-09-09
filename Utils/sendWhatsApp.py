import pyautogui, pyperclip, time

INPUT_X = 915
INPUT_Y = 575

def send_whatsapp_message(message):
    pyautogui.click(INPUT_X, INPUT_Y)
    time.sleep(0.5)

    pyperclip.copy(message)
    pyautogui.hotkey("ctrl", "v")

    time.sleep(0.5)
    pyautogui.press("enter")
