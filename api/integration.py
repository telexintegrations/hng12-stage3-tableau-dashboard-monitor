from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, UTC

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

        integration_data = {
            "data": {
                "date": {
                    "created_at": "2025-02-22",
                    "updated_at": current_time
                },
                "descriptions": {
                    "app_name": "Tableau Monitor",
                    "app_description": "Detects failures or slow loading of Tableau reports using Tableau Server Logs. Monitors dashboard performance and sends alerts when load times exceed thresholds or when errors occur.",
                    "app_logo": "data:image/png;base64,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",
                    "app_url": "https://hng12-stage3-tableau-dashboard-monitor.vercel.app",
                    "background_color": "#fff"
                },
                "is_active": True,
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
                        "required": True,
                        "default": "*/1 * * * *"  # Run every minute
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
