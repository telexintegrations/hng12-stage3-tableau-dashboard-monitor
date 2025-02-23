from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, UTC

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Get current date in YYYY-MM-DD format
        current_date = datetime.now(UTC).strftime('%Y-%m-%d')

        # Integration data with exact format
        integration_data = {
            "data": {
                "date": {
                    "created_at": "2025-02-22",
                    "updated_at": "2025-02-22"
                },
                "descriptions": {
                    "app_name": "Tableau Monitor",
                    "app_description": "Detects failures or slow loading of Tableau reports using Tableau Server Logs. Monitors dashboard performance and sends alerts when load times exceed thresholds or when errors occur.",
                    "app_logo": "https://img.icons8.com/color/48/tableau-software.png",
                    "app_url": "https://hng12-stage3-tableau-dashboard-monitor.vercel.app",
                    "background_color": "#fff"
                },
                "is_active": true,
                "integration_type": "interval",
                "integration_category": "Monitoring & Logging",
                "key_features": [
                    "Real-time dashboard load time monitoring",
                    "Automatic failure detection",
                    "Performance threshold alerts",
                    "Error log analysis"
                ],
                "author": "cod_emminex",
                "settings": [
                    {
                        "label": "Time interval",
                        "type": "multi-select",
                        "required": true,
                        "default": "/1 * * * *"
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
        # Handle CORS preflight request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
