from Functions.watchReportResolved import resolved_watcher
from Functions.watchNewReport import latest_watcher
import threading, time
from threading import Lock

whatsapp_lock = Lock()

recently_resolved_channels = {}

threading.Thread(
    target=resolved_watcher,
    args=(15, whatsapp_lock, recently_resolved_channels),
    daemon=True
).start()

threading.Thread(
    target=latest_watcher,
    args=(15, whatsapp_lock),
    daemon=True
).start()

print("[✅] Script started. Watchers are running in background.")
while True:
    time.sleep(60)
