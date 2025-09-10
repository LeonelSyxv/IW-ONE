import pyautogui, pyperclip, time
from collections import defaultdict
from Database.db import get_connection
from Utils.sendWhatsApp import INPUT_X, INPUT_Y

pyautogui.FAILSAFE = False

def latest_watcher(poll_interval=30, whatsapp_lock=None):
    print("Listening for latest 'Momentary' report in 'Revision' status...")

    processed_report_ids = set()
    start_time = None

    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT created_at
                FROM reports
                WHERE type = 'Momentary' AND status = 'Revision'
                ORDER BY created_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                start_time = row[0]
                print(f"Startup initialized. Ignoring reports created at or before: {start_time}")
    except Exception as e:
        print(f"Error fetching initial report timestamp: {e}")

    while True:
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT MAX(updated_at)
                    FROM reports
                    WHERE status = 'Resolved'
                """)
                last_resolved_time = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT id, reviewed_by, created_at
                    FROM reports
                    WHERE type = 'Momentary' AND status = 'Revision'
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()

                if not row:
                    time.sleep(poll_interval)
                    continue

                report_id, reviewed_by, created_at = row

                if start_time and created_at <= start_time:
                    processed_report_ids.add(report_id)
                    time.sleep(poll_interval)
                    continue

                if last_resolved_time and created_at <= last_resolved_time:
                    processed_report_ids.add(report_id)
                    time.sleep(poll_interval)
                    continue

                if report_id in processed_report_ids:
                    time.sleep(poll_interval)
                    continue

                print(f"New report detected: ID {report_id}")

                cursor.execute("""
                    SELECT 
                        c.number, 
                        c.name, 
                        rd.description, 
                        rd.protocol, 
                        rd.media, 
                        s.name AS stage_name
                    FROM report_details rd
                    JOIN channels c ON c.id = rd.channel_id
                    JOIN stages s ON s.id = rd.stage_id
                    WHERE rd.report_id = %s
                """, (report_id,))
                results = cursor.fetchall()

                if not results:
                    processed_report_ids.add(report_id)
                    time.sleep(poll_interval)
                    continue

                grouped_by_stage = defaultdict(list)

                for number, name, description, protocol, media, stage in results:
                    desc = description.strip() if description else "Sin descripción"
                    issue = f"Problema de *{media}*" if media else "Sin A/V"
                    additional = f" ({issue} en *{protocol}*)" if protocol else f" ({issue})"

                    grouped_by_stage[stage].append(
                        (f"*Canal {number} {name}*", desc + additional)
                    )

                for stage, channel_list in grouped_by_stage.items():

                    sorted_lines = sorted(
                        [f"• {label}: {text}" for label, text in channel_list],
                        key=lambda line: int(line.split("Canal ")[1].split(" ")[0])
                    )

                    if not sorted_lines:
                        continue

                    header = f"⚠️ Nuevos fallos detectados en *{stage}* *({len(sorted_lines)} Canal{'es' if len(sorted_lines) != 1 else ''})*:"
                    body = "\n\n".join(sorted_lines)
                    message = f"{header}\n\n{body}\n\nEn revisión por *{reviewed_by}*."

                    if whatsapp_lock:
                        with whatsapp_lock:
                            pyautogui.hotkey("ctrl", "tab")
                            time.sleep(2)
                            pyautogui.click(INPUT_X, INPUT_Y)
                            time.sleep(0.5)
                            pyperclip.copy(message)
                            pyautogui.hotkey("ctrl", "v")
                            time.sleep(1)
                            pyautogui.press("enter")
                            pyautogui.hotkey("ctrl", "tab")
                            time.sleep(2)

                    print(f"WhatsApp message sent for stage '{stage}':\n{message}\n")

                processed_report_ids.add(report_id)

        except Exception as e:
            print(f"Error in latest_momentary_revision_watcher: {e}")

        time.sleep(poll_interval)
