import requests
import time
from datetime import datetime, UTC
import os

def monitor_uptime():
    url = "https://hng12-stage3-tableau-dashboard-monitor.onrender.com/"
    log_file = "uptime_log.txt"
    
    while True:
        try:
            current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            response = requests.get(url)
            
            status = "UP" if response.status_code == 200 else f"DOWN ({response.status_code})"
            log_entry = f"{current_time} - Server {status}\n"
            
            # Print to console
            print(log_entry.strip())
            
            # Write to log file
            with open(log_file, "a") as f:
                f.write(log_entry)
            
            # If server is down, try to wake it up
            if response.status_code != 200:
                print(f"{current_time} - Attempting to wake up server...")
                requests.get(f"{url}api/monitor")
                
        except Exception as e:
            error_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            error_entry = f"{error_time} - ERROR: {str(e)}\n"
            
            print(error_entry.strip())
            with open(log_file, "a") as f:
                f.write(error_entry)
        
        # Wait 5 minutes before next check
        time.sleep(300)

if __name__ == "__main__":
    print("Starting uptime monitor...")
    monitor_uptime()
