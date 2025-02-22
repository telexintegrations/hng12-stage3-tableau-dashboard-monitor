from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, UTC
import tableauserverclient as TSC
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Configuration
            server_url = os.getenv('TABLEAU_SERVER_HOST', 'https://dub01.online.tableau.com')
            site_name = os.getenv('TABLEAU_SITE_NAME', 'emminexy-f537b42aad')
            token_name = os.getenv('TABLEAU_TOKEN_NAME', 'TelescopeMonitoring')
            token = os.getenv('TABLEAU_API_TOKEN')
            webhook_url = "https://ping.telex.im/v1/webhooks/019528ca-ae9c-79d7-a3ed-2dc5866df56a"

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

                response_data = {
                    "success": True,
                    "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                    "user": "cod-emminex",
                    "total_views": len(all_views),
                    "server_url": server_url,
                    "site_name": site_name,
                    "views": [
                        {
                            "name": view.name,
                            "id": view.id,
                            "created_at": view.created_at.strftime('%Y-%m-%d %H:%M:%S') if view.created_at else None
                        }
                        for view in all_views
                    ]
                }

                # Send webhook notification
                webhook_payload = {
                    "event_name": "tableau_monitor_check",
                    "username": "cod-emminex",
                    "status": "success",
                    "message": f"Successfully checked {len(all_views)} views"
                }

                requests.post(
                    webhook_url,
                    json=webhook_payload,
                    headers={"Content-Type": "application/json"}
                )

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            error_data = {
                "success": False,
                "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                "user": "cod-emminex",
                "error": str(e)
            }

            # Send webhook error notification
            try:
                requests.post(
                    webhook_url,
                    json={
                        "event_name": "tableau_monitor_error",
                        "username": "cod-emminex",
                        "status": "error",
                        "message": f"Error: {str(e)}"
                    },
                    headers={"Content-Type": "application/json"}
                )
            except:
                pass

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
