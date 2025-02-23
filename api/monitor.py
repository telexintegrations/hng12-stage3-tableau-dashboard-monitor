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
            webhook_url = "https://ping.telex.im/v1/webhooks/01952fe5-d4fd-7bde-bcd2-7a2fd2c55c87"

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

                # Format message
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

                # Send webhook notification in correct format
                webhook_data = {
                    "message": message,
                    "username": "Tableau Monitor",
                    "event_name": "tableau_monitor_check",
                    "status": "error" if error_count > 0 else "success"
                }

                requests.post(
                    webhook_url,
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

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, indent=2).encode())

        except Exception as e:
            error_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

            # Send webhook error notification in correct format
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
                    webhook_url,
                    json=webhook_data,
                    headers={"Content-Type": "application/json"}
                )
            except:
                pass

            # Response for API endpoint
            error_data = {
                "success": False,
                "timestamp": error_time,
                "user": "cod-emminex",
                "error": str(e)
            }

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
