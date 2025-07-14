import psutil
import os
import sys
import time
import logging
from winotify import Notification
from playsound import playsound

# ---------------------- Setup Logging ----------------------
appdata = os.getenv('APPDATA') or os.path.expanduser('~\\AppData\\Roaming')
log_dir = os.path.join(appdata, 'BatteryNotifier')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, 'battery_log.txt')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log(msg):
    print(msg)
    logging.info(msg)

# ---------------------- Prevent Multiple Instances ----------------------
def is_already_running():
    current_pid = os.getpid()
    current_exe = os.path.abspath(sys.argv[0])

    for proc in psutil.process_iter(['pid', 'exe']):
        try:
            if proc.info['pid'] != current_pid and proc.info['exe']:
                if os.path.abspath(proc.info['exe']) == current_exe:
                    log(f"⚠️ Found already running instance at: {proc.info['exe']} (PID {proc.info['pid']})")
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False

# ---------------------- Notification Function ----------------------
def show_notification_and_sound(percent):
    log(f"🔔 Alert triggered at battery {percent}%")

    wav_exists = os.path.exists("battery_alert.wav")
    log("🎵 WAV file exists: " + str(wav_exists))

    toast = Notification(
        app_id="Battery Notifier",
        title="Battery Charged!",
        msg=f"Battery is at {percent}%. Please unplug the charger.",
        icon="icon.ico"  # this line must be set if you want icon in toast
    )

    toast.set_audio(None, loop=False)
    toast.show()

    if wav_exists:
        try:
            playsound("battery_alert.wav")
        except Exception as e:
            log(f"❌ Sound playback failed: {e}")
    else:
        log("⚠️ Skipping sound playback — file not found.")

# ---------------------- Main Function ----------------------
def main():
    # Uncomment below if you want to prevent duplicates
    # if is_already_running():
    #     log("⚠️ Battery Monitor is already running. Exiting.")
    #     sys.exit(0)

    log("✅ Battery Monitor started.")

    alert_triggered = False
    last_alert_time = 0
    prev_plugged = None

    while True:
        try:
            battery = psutil.sensors_battery()
            if battery is None:
                log("❌ No battery detected. Exiting...")
                break

            percent = battery.percent
            plugged = battery.power_plugged
            current_time = time.time()

            if prev_plugged is not None:
                if plugged and not prev_plugged:
                    log(f"🔌 Charger PLUGGED IN at battery {percent}%")
                elif not plugged and prev_plugged:
                    log(f"🔋 Charger UNPLUGGED at battery {percent}%")

            prev_plugged = plugged

            if plugged and percent >= 80:
                if not alert_triggered or (current_time - last_alert_time >= 120):
                    show_notification_and_sound(percent)
                    alert_triggered = True
                    last_alert_time = current_time
                else:
                    log("⏳ Waiting for re-alert window...")
            elif not plugged:
                if alert_triggered:
                    log(f"🔌 Charger unplugged. Resetting alert system at battery {percent}%")
                alert_triggered = False
                last_alert_time = 0

            time.sleep(10)

        except Exception:
            logging.exception("💥 Unhandled exception in battery monitor:")
            time.sleep(10)

# ---------------------- Entry Point ----------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("🛑 Battery Monitor stopped by user.")
        sys.exit(0)
