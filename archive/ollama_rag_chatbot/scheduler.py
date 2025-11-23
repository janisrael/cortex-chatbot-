from apscheduler.schedulers.background import BackgroundScheduler
import os
from learning import main

from subprocess import Popen, PIPE
import time
from datetime import datetime, timedelta


# Get absolute path to current directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Build path to learner.py in the same folder
learner_path = os.path.join(base_dir, "learning.py")

log_file_path = os.path.join(base_dir, "chatbot_learn.log")

print(f"[Scheduler] Running {learner_path}...")
print(f"[Scheduler] Writing logs to {log_file_path}...")


def run_learner():
    # print("[Scheduler] Running learner.py...")
    # process = Popen(["python3", learner_path], stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    stdout = main()
    if stdout:
        with open(log_file_path, "a") as f:
            f.write("[Error] ")
    # if stderr:
    #     print("[Error]", stderr.decode())

def start():
    scheduler = BackgroundScheduler()

    # Run every day at 1:00 AM
    scheduler.add_job(run_learner, 'cron', hour=1, minute=0)

    # 🔁 Run immediately once for testing
    scheduler.add_job(run_learner, 'date', run_date=datetime.now() + timedelta(seconds=2))

    scheduler.start()
    print("🔁 Scheduler started. Learner will run now and daily at 1:00 AM.")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped.")

if __name__ == "__main__":
    start()
