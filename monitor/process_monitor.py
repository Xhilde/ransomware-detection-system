import psutil
import time


# 🔹 Get processes consuming high CPU
def get_high_cpu_processes(cpu_threshold=20):
    suspicious = []

    # First call to initialize CPU percent calculation
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1)  # Allow CPU % calculation window

    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            if proc.info['cpu_percent'] > cpu_threshold:
                suspicious.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return suspicious


# 🔹 Get recently started processes
def get_recent_processes(time_window=60):
    current_time = time.time()
    recent = []

    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
        try:
            if current_time - proc.info['create_time'] < time_window:
                recent.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return recent


# 🔹 Calculate suspicion score
def calculate_suspicion_score(high_cpu, recent):
    score = 0
    score += len(high_cpu) * 2
    score += len(recent)
    return score