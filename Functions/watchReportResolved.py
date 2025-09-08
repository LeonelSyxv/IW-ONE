import pyautogui, pyperclip, time
from datetime import datetime
from Database.db import get_connection
from Utils.sendWhatsApp import INPUT_X, INPUT_Y

pyautogui.FAILSAFE = False

def resolved_watcher(poll_interval=30, whatsapp_lock=None, recently_resolved_channels=None):
    print("Starting listener for status changes to 'Resolved'...")

    previous_revision = {}
    initialized = False

    while True:
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.id, c.number, c.name, rd.media, rd.protocol
                    FROM reports r
                    JOIN report_details rd ON rd.report_id = r.id
                    JOIN channels c ON c.id = rd.channel_id
                    WHERE r.status = 'Revision' AND r.type = 'Momentary'
                """)
                current_revision = {
                    row[0]: {
                        "number": row[1],
                        "name": row[2],
                        "media": row[3],
                        "protocol": row[4]
                    }
                    for row in cursor.fetchall()
                }

                if initialized:
                    resolved_ids = set(previous_revision.keys()) - set(current_revision.keys())

                    for channel_id in resolved_ids:
                        channel = previous_revision[channel_id]
                        number = channel["number"]
                        name = channel["name"]
                        media = channel["media"]
                        protocol = channel["protocol"]

                        message = (
                            f"✅ *Canal {number} {name}*: Ya se encuentra operando correctamente "
                            f"con *{media}* en *{protocol}*."
                        )

                        with whatsapp_lock:
                            pyautogui.click(INPUT_X, INPUT_Y)
                            time.sleep(0.5)
                            pyperclip.copy(message)
                            pyautogui.hotkey("ctrl", "v")
                            time.sleep(1)
                            pyautogui.press("enter")
                        print(f"WhatsApp message sent: {message}")

                        if recently_resolved_channels is not None:
                            canal_key = f"{number}-{name}"
                            recently_resolved_channels[canal_key] = datetime.now()

                else:
                    print("First watcher cycle, initializing without sending messages.")
                    initialized = True

                previous_revision = current_revision

        except Exception as e:
            print(f"Error in resolved_watcher: {e}")

        time.sleep(poll_interval)
