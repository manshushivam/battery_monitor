import psutil
import subprocess
import time
import os
import sys
import logging

# ---------------------- Setup Logging ----------------------
appdata = os.getenv('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
log_dir = os.path.join(appdata, 'BatteryNotifier')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'launcher_log.txt')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

# ---------------- Prevent Multiple Launcher Instances ----------------
def is_already_running():
    current_pid = os.getpid()
    current_exe = os.path.abspath(sys.argv[0])
    log(f"Current PID: {current_pid}, Executable: {current_exe}")
    for proc in psutil.process_iter(['pid', 'exe']):
        log(f"Checking process: PID {proc.info['pid']}, Executable: {proc.info.get('exe', 'N/A')}")
        try:
            if proc.info['pid'] != current_pid and proc.info['exe']:
                if os.path.abspath(proc.info['exe']) == current_exe:
                    log(f"⚠️ Found already running launcher instance at: {proc.info['exe']} (PID {proc.info['pid']})")
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False

# if is_already_running():
#     log("⚠️ Launcher is already running. Exiting.")
#     sys.exit(0)

# ---------------------------------------------------------------------

log("🚀 Launcher started.")
launched = False
prev_plugged = None

while True:
    log("🔄 Checking battery status...")
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            log("❌ No battery detected. Exiting launcher.")
            break

        plugged = battery.power_plugged

        # Log charger plug/unplug event
        if prev_plugged is not None:
            if plugged and not prev_plugged:
                log(f"🔌 Charger plugged in — monitoring started.")
            elif not plugged and prev_plugged:
                log(f"🔋 Charger unplugged — monitoring paused.")

        prev_plugged = plugged

        if plugged and not launched:
            process = subprocess.Popen(["battery_monitor.exe"])
            log(f"✅ Launched battery_monitor.exe (PID {process.pid})")
            launched = True
        elif not plugged:
            launched = False

        time.sleep(10)

    except Exception as e:
        logging.exception("💥 Unhandled exception in launcher:")
        time.sleep(10)
