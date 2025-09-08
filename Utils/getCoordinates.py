from pynput import mouse, keyboard
import threading, time

coordinates = []
finish = False

last_click = 0
double_click_threshold = 0.3

def on_click(x, y, button, pressed):
    global last_click
    if pressed:
        now = time.time()
        time_between_clicks = now - last_click
        last_click = now

        if time_between_clicks < double_click_threshold:
            click_type = "Double click"
        elif button.name == "right":
            click_type = "Right click"
        else:
            click_type = "Click"

        print(f"{click_type} at: ({x}, {y})")
        coordinates.append((x, y, click_type))

def on_press(key):
    global finish
    if key == keyboard.Key.esc:
        finish = True
        print("\nRecording finished.")
        print("Captured coordinates:")
        for coord in coordinates:
            print(coord)
        return False

def listen_mouse():
    with mouse.Listener(on_click=on_click) as listener:
        while not finish:
            time.sleep(0.1)
        listener.stop()

def listen_keyboard():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

print("Click anywhere. Press ESC to finish...\n")
mouse_thread = threading.Thread(target=listen_mouse)
mouse_thread.start()
listen_keyboard()
