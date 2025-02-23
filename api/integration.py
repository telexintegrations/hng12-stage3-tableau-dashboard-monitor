from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, UTC

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        current_time = datetime.now(UTC).strftime('%Y-%m-%d')

        integration_data = {
            "data": {
                "date": {
                    "created_at": current_time,
                    "updated_at": current_time
                },
                "descriptions": {
                    "app_name": "Tableau Monitor",
                    "app_description": "Detects failures or slow loading of Tableau reports using Tableau Server Logs. Monitors dashboard performance and sends alerts when load times exceed thresholds or when errors occur.",
                    "app_logo": "https://img.icons8.com/color/48/tableau-software.png",
                    "app_url": "https://hng12-stage3-tableau-dashboard-monitor.vercel.app",
                    "background_color": "#fff"
                },
                "integration_type": "interval",
                "integration_category": "Monitoring & Logging",
                "is_active": True,
                "key_features": [
                    "Real-time dashboard load time monitoring",
                    "Automatic failure detection",
                    "Performance threshold alerts",
                    "Error log analysis"
                ],
                "settings": [
                    {
                        "label": "interval",
                        "type": "text",
                        "required": True,
                        "default": "*/1 * * * *"
                    },
                    {
                        "label": "Load Time Threshold",
                        "type": "number",
                        "required": True,
                        "default": "10",
                        "description": "Maximum acceptable load time in seconds"
                    }
                ],
                "target_url": "https://ping.telex.im/v1/webhooks/01952fe5-d4fd-7bde-bcd2-7a2fd2c55c87",
                "tick_url": "https://hng12-stage3-tableau-dashboard-monitor.vercel.app/api/monitor"
            }
        }

        # Set response headers with CORS
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        # Send response with exact formatting
        self.wfile.write(json.dumps(integration_data, indent=2).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
