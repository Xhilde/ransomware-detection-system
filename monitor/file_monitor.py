import time
import os
from collections import deque
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import logger
import process_monitor

# ==============================
# CONFIGURATION
# ==============================

TIME_WINDOW = 60  # seconds
THRESHOLD_FILES = 10
EXTENSION_CHANGE_THRESHOLD = 5

# ==============================
# MONITOR CLASS
# ==============================

class RansomwareMonitor(FileSystemEventHandler):

    def __init__(self):
        self.file_events = deque()
        self.extension_events = deque()

    def clean_old_events(self):
        current_time = time.time()

        while self.file_events and current_time - self.file_events[0] > TIME_WINDOW:
            self.file_events.popleft()

        while self.extension_events and current_time - self.extension_events[0] > TIME_WINDOW:
            self.extension_events.popleft()

    # 🔹 Detect file creation
    def on_created(self, event):
        if event.is_directory:
            return

        if self.is_valid_path(event.src_path):
            print(f"[FILE CREATED] {event.src_path}")
            logger.log_info(f"File created: {event.src_path}")
            self.file_events.append(time.time())

    # 🔹 Detect file modification
    def on_modified(self, event):
        if event.is_directory:
            return

        if self.is_valid_path(event.src_path):
            print(f"[FILE MODIFIED] {event.src_path}")
            logger.log_info(f"File modified: {event.src_path}")
            self.file_events.append(time.time())

    # 🔹 Detect extension change (rename)
    def on_moved(self, event):
        if event.is_directory:
            return

        old_ext = os.path.splitext(event.src_path)[1]
        new_ext = os.path.splitext(event.dest_path)[1]

        if old_ext != new_ext and self.is_valid_path(event.dest_path):
            print(f"[EXTENSION CHANGE] {event.dest_path} | {old_ext} → {new_ext}")
            logger.log_warning(
                f"Extension change: {event.dest_path} | {old_ext} → {new_ext}"
            )
            self.extension_events.append(time.time())

    # 🔹 Ignore noise folders
    def is_valid_path(self, path):
        ignored_keywords = ['.vscode', 'AppData', '$Recycle.Bin', 'alerts.log', 'logs']
        return not any(keyword in path for keyword in ignored_keywords)

    # 🔹 Check detection thresholds
    def check_thresholds(self):
        self.clean_old_events()

        # File burst detection
        if len(self.file_events) >= THRESHOLD_FILES:
            print("\n⚠️ RANSOMWARE-LIKE FILE ACTIVITY DETECTED")
            print(f"Files affected in last {TIME_WINDOW}s: {len(self.file_events)}\n")

            logger.log_warning(
                f"File burst detected: {len(self.file_events)} files in {TIME_WINDOW}s"
            )

            # Process correlation
            high_cpu = process_monitor.get_high_cpu_processes()
            recent = process_monitor.get_recent_processes()
            score = process_monitor.calculate_suspicion_score(high_cpu, recent)

            print("High CPU Processes:", high_cpu)
            print("Recently Started Processes:", recent)
            print("Suspicion Score:", score)

            logger.log_info(f"High CPU Processes: {high_cpu}")
            logger.log_info(f"Recent Processes: {recent}")
            logger.log_warning(f"Suspicion Score: {score}")

        # Extension change detection
        if len(self.extension_events) >= EXTENSION_CHANGE_THRESHOLD:
            print("\n🚨 HIGH SEVERITY: MASS EXTENSION CHANGES DETECTED")
            print(
                f"Extension changes in last {TIME_WINDOW}s: {len(self.extension_events)}\n"
            )

            logger.log_critical(
                f"Mass extension changes detected: {len(self.extension_events)} in {TIME_WINDOW}s"
            )


# ==============================
# MAIN (Simple Execution)
# ==============================

if __name__ == "__main__":

    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

    event_handler = RansomwareMonitor()
    observer = Observer()
    observer.schedule(event_handler, desktop_path, recursive=True)

    observer.start()

    print(f"📁 Monitoring started on: {desktop_path}")

    try:
        while True:
            event_handler.check_thresholds()
            print(
                f"Monitoring... Files in last {TIME_WINDOW}s: {len(event_handler.file_events)}"
            )
            time.sleep(5)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()