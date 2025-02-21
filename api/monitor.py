from http.server import BaseHTTPRequestHandler
import os
import sys
import json
from datetime import datetime, UTC

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tableau_monitor import TableauMonitor

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Initialize the monitor
            monitor = TableauMonitor()

            # Run the dashboard check
            success = monitor.check_dashboards()

            # Prepare response
            response_data = {
                "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                "user": "cod-emminex",
                "success": success,
                "message": "Tableau monitoring completed successfully" if success else "Monitoring failed"
            }

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            error_response = {
                "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                "user": "cod-emminex",
                "success": False,
                "error": str(e)
            }
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

