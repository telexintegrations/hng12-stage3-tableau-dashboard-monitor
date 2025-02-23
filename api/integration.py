from flask import Flask, jsonify
from datetime import datetime, UTC

app = Flask(__name__)

@app.route('/api/integrations')
def get_integration():
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
                "app_url": "https://tableau-monitor.onrender.com",
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
                    "default": "*/40 * * * *"
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
            "tick_url": "https://tableau-monitor.onrender.com/api/monitor"
        }
    }

    return jsonify(integration_data), 200, {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
