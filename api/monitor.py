from flask import Flask, jsonify, request
import json
import os
from datetime import datetime, UTC
import tableauserverclient as TSC
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Tableau Monitor API is running",
        "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
        "endpoints": [
            "/api/integration",
            "/api/monitor"
        ]
    })

@app.route('/api/integration', methods=['GET'])
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
                "app_url": "https://hng12-stage3-tableau-dashboard-monitor.onrender.com",
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
            "tick_url": "https://hng12-stage3-tableau-dashboard-monitor.onrender.com/api/monitor"
        }
    }

    return jsonify(integration_data)

@app.route('/api/monitor', methods=['GET', 'POST'])
def monitor():
    try:
        # Configuration
        server_url = os.getenv('TABLEAU_SERVER_HOST', 'https://dub01.online.tableau.com')
        site_name = os.getenv('TABLEAU_SITE_NAME', 'emminexy-f537b42aad')
        token_name = os.getenv('TABLEAU_TOKEN_NAME', 'TelescopeMonitoring')
        token = os.getenv('TABLEAU_API_TOKEN')
        webhook_url = "https://ping.telex.im/v1/webhooks/01952fe5-d4fd-7bde-bcd2-7a2fd2c55c87"

        # Get return_url from POST data if available
        if request.method == 'POST':
            data = request.get_json()
            return_url = data.get('return_url', webhook_url)
        else:
            return_url = webhook_url

        # Initialize Tableau connection
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=token_name,
            personal_access_token=token,
            site_id=site_name
        )

        server = TSC.Server(
            server_url,
            use_server_version=False
        )
        server.version = '3.16'

        # Test connection and get views
        with server.auth.sign_in_with_personal_access_token(tableau_auth):
            all_views = list(TSC.Pager(server.views))

            # Get additional view details
            view_details = []
            error_count = 0
            for view in all_views:
                try:
                    server.views.populate_preview_image(view)
                    status = "active"
                except:
                    status = "error"
                    error_count += 1

                view_details.append({
                    "name": view.name,
                    "id": view.id,
                    "status": status,
                    "created_at": view.created_at.strftime('%Y-%m-%d %H:%M:%S') if view.created_at else None,
                    "project_name": view.project_name if hasattr(view, 'project_name') else None
                })

            # Format message for webhook
            views_list = "\n".join([
                f"{i+1}. {view['name']} ({view['project_name'] or 'No Project'}) - {view['status'].upper()}"
                for i, view in enumerate(view_details)
            ])

            current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            message = (
                f"Tableau Monitor Check - {current_time}\n"
                f"Server: {server_url}\n"
                f"Site: {site_name}\n"
                f"Total Views: {len(all_views)}\n"
                f"Active Views: {len(all_views) - error_count}\n"
                f"Error Views: {error_count}\n\n"
                f"Views Status:\n{views_list}"
            )

            # Send webhook notification
            webhook_data = {
                "message": message,
                "username": "Tableau Monitor",
                "event_name": "tableau_monitor_check",
                "status": "error" if error_count > 0 else "success"
            }

            # Send to the appropriate URL
            requests.post(
                return_url,
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )

            # Response for API endpoint
            response_data = {
                "success": True,
                "timestamp": current_time,
                "user": "cod-emminex",
                "total_views": len(all_views),
                "server_url": server_url,
                "site_name": site_name,
                "views": view_details,
                "errors_found": error_count
            }

            return jsonify(response_data)

    except Exception as e:
        error_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

        # Send webhook error notification
        try:
            error_message = (
                f"Tableau Monitor Error - {error_time}\n"
                f"Server: {os.getenv('TABLEAU_SERVER_HOST', 'N/A')}\n"
                f"Site: {os.getenv('TABLEAU_SITE_NAME', 'N/A')}\n"
                f"Error: {str(e)}"
            )

            webhook_data = {
                "message": error_message,
                "username": "Tableau Monitor",
                "event_name": "tableau_monitor_error",
                "status": "error"
            }

            requests.post(
                return_url if 'return_url' in locals() else webhook_url,
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )
        except:
            pass

        error_data = {
            "success": False,
            "timestamp": error_time,
            "user": "cod-emminex",
            "error": str(e)
        }

        return jsonify(error_data), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
