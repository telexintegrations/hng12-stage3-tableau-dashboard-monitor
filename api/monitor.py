from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, UTC
import tableauserverclient as TSC
import requests

class handler(BaseHTTPRequestHandler):
    def send_webhook_notification(self, event_type, data, views_data=None):
        """Send enhanced webhook notification"""
        webhook_url = "https://ping.telex.im/v1/webhooks/019528ca-ae9c-79d7-a3ed-2dc5866df56a"
        current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

        webhook_payload = {
            "event_name": f"tableau_monitor_{event_type}",
            "username": "cod-emminex",
            "timestamp": current_time,
            "status": data.get("status", "info"),
            "details": {
                "message": data.get("message", ""),
                "monitor_info": {
                    "total_views": data.get("total_views", 0),
                    "server_url": data.get("server_url", ""),
                    "site_name": data.get("site_name", ""),
                    "check_time": current_time
                }
            }
        }

        # Add views data if available
        if views_data:
            webhook_payload["details"]["views"] = [
                {
                    "name": view.name,
                    "id": view.id,
                    "created_at": view.created_at.strftime('%Y-%m-%d %H:%M:%S') if view.created_at else None,
                    "project": view.project_name if hasattr(view, 'project_name') else None,
                    "status": "active"
                }
                for view in views_data[:5]  # Include first 5 views
            ]

            webhook_payload["details"]["views_summary"] = {
                "total": len(views_data),
                "projects": len(set(v.project_name for v in views_data if hasattr(v, 'project_name'))),
                "last_checked": current_time
            }

        try:
            response = requests.post(
                webhook_url,
                json=webhook_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 202
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return False

    def do_GET(self):
        try:
            # Configuration
            server_url = os.getenv('TABLEAU_SERVER_HOST', 'https://dub01.online.tableau.com')
            site_name = os.getenv('TABLEAU_SITE_NAME', 'emminexy-f537b42aad')
            token_name = os.getenv('TABLEAU_TOKEN_NAME', 'TelescopeMonitoring')
            token = os.getenv('TABLEAU_API_TOKEN')

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
                for view in all_views:
                    try:
                        server.views.populate_preview_image(view)
                    except:
                        pass

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
                            "created_at": view.created_at.strftime('%Y-%m-%d %H:%M:%S') if view.created_at else None,
                            "updated_at": view.updated_at.strftime('%Y-%m-%d %H:%M:%S') if view.updated_at else None,
                            "project_name": view.project_name if hasattr(view, 'project_name') else None,
                            "size": len(view.preview_image) if hasattr(view, 'preview_image') else 0
                        }
                        for view in all_views
                    ],
                    "status": "success",
                    "message": f"Successfully monitored {len(all_views)} views"
                }

                # Send enhanced webhook notification
                self.send_webhook_notification(
                    "check",
                    response_data,
                    all_views
                )

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())

        except Exception as e:
            error_data = {
                "success": False,
                "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                "user": "cod-emminex",
                "error": str(e),
                "status": "error",
                "message": f"Monitoring failed: {str(e)}"
            }

            # Send enhanced error webhook notification
            self.send_webhook_notification("error", error_data)

            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(error_data, indent=2).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
