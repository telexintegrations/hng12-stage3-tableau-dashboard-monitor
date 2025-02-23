from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, UTC
import tableauserverclient as TSC
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        start_time = datetime.now(UTC)
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
                        "project_name": view.project_name if hasattr(view, 'project_name') else "No Project"
                    })

                end_time = datetime.now(UTC)
                check_duration = (end_time - start_time).total_seconds()

                response_data = {
                    "success": True,
                    "timestamp": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "user": "cod-emminex",
                    "total_views": len(all_views),
                    "server_url": server_url,
                    "site_name": site_name,
                    "views": view_details,
                    "check_duration": f"{check_duration:.2f}s",
                    "errors_found": error_count
                }

                # Create detailed message for webhook with all views
                status = "warning" if error_count > 0 else "success"

                # Build the views list string
                views_list = "\n".join([
                    f"{i+1}. {view['name']} ({view['project_name']}) - {view['status']}"
                    for i, view in enumerate(view_details)
                ])

                message = (
                    f"Monitor Check ({end_time.strftime('%Y-%m-%d %H:%M:%S')})\n"
                    f"Total Views: {len(all_views)}\n"
                    f"Active Views: {len(all_views) - error_count}\n"
                    f"Error Views: {error_count}\n"
                    f"Check Duration: {check_duration:.2f}s\n"
                    f"Projects: {len(set(v['project_name'] for v in view_details))}\n\n"
                    f"Views List:\n{views_list}"
                )

                # Send webhook notification
                webhook_payload = {
                    "event_name": "tableau_monitor_check",
                    "username": "cod-emminex",
                    "status": status,
                    "message": message
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
            error_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')
            error_data = {
                "success": False,
                "timestamp": error_time,
                "user": "cod-emminex",
                "error": str(e)
            }

            # Send webhook error notification with more detail
            try:
                error_message = (
                    f"Monitor Error ({error_time})\n"
                    f"Error: {str(e)}\n"
                    f"Server: {os.getenv('TABLEAU_SERVER_HOST', 'N/A')}\n"
                    f"Site: {os.getenv('TABLEAU_SITE_NAME', 'N/A')}"
                )

                requests.post(
                    webhook_url,
                    json={
                        "event_name": "tableau_monitor_error",
                        "username": "cod-emminex",
                        "status": "error",
                        "message": error_message
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
