import os
import csv
from datetime import datetime

def write_to_log_csv(action: str, user: str, user_id: int, moderator: str, moderator_id: int, reason: str = ""):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Ensure directory exists
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(base_dir, "ban_logs")
    os.makedirs(logs_dir, exist_ok=True)

    file_path = os.path.join(logs_dir, "logs.csv")

    # Check if file exists (to write header once)
    write_header = not os.path.exists(file_path)

    # Write to CSV
    with open(file_path, "a", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        if write_header:
            writer.writerow(["timestamp", "action", "user", "user_id", "moderator", "moderator_id", "reason"])
        writer.writerow([timestamp, action, user, user_id, moderator, moderator_id, reason])
