from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime, UTC
import tableauserverclient as TSC
import requests

class handler(BaseHTTPRequestHandler):
    def send_webhook(self, event_type, data):
        """Send detailed webhook notification"""
        webhook_url = "https://ping.telex.im/v1/webhooks/019528ca-ae9c-79d7-a3ed-2dc5866df56a"
        current_time = datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')

        # Format views data for webhook
        views_summary = []
        if data.get('views'):
            for view in data['views']:
                view_info = {
                    "name": view['name'],
                    "status": view.get('status', 'unknown'),
                    "load_time": view.get('load_time', 'N/A'),
                    "last_updated": view.get('updated_at', 'N/A')
                }
                views_summary.append(view_info)

        webhook_data = {
            "event_name": f"tableau_monitor_{event_type}",
            "username": "cod-emminex",
            "status": data.get('status', 'info'),
            "timestamp": current_time,
            "message": {
                "summary": data.get('message', 'Tableau monitoring check completed'),
                "total_views": data.get('total_views', 0),
                "server_url": data.get('server_url', ''),
                "site_name": data.get('site_name', ''),
                "views": views_summary[:5],  # Send first 5 views for brevity
                "performance": {
                    "slow_views": data.get('slow_views', 0),
                    "error_views": data.get('error_views', 0),
                    "average_load_time": data.get('avg_load_time', 'N/A')
                },
                "monitoring_details": {
                    "check_time": current_time,
                    "threshold": data.get('threshold', 10),
                    "check_duration": data.get('check_duration', 'N/A')
                }
            }
        }

        try:
            response = requests.post(
                webhook_url,
                json=webhook_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            return response.status_code == 202
        except Exception as e:
            print(f"Webhook error: {str(e)}")
            return False

    def do_GET(self):
        start_time = datetime.now(UTC)
        try:
            # Configuration
            config = {
                'server_url': os.getenv('TABLEAU_SERVER_HOST', 'https://dub01.online.tableau.com'),
                'site_name': os.getenv('TABLEAU_SITE_NAME', 'emminexy-f537b42aad'),
                'token_name': os.getenv('TABLEAU_TOKEN_NAME', 'TelescopeMonitoring'),
                'token': os.getenv('TABLEAU_API_TOKEN'),
                'threshold': int(os.getenv('LOAD_TIME_THRESHOLD', 10))
            }

            # Initialize Tableau connection
            tableau_auth = TSC.PersonalAccessTokenAuth(
                token_name=config['token_name'],
                personal_access_token=config['token'],
                site_id=config['site_name']
            )

            server = TSC.Server(
                config['server_url'],
                use_server_version=False
            )
            server.version = '3.16'

            views_data = []
            slow_views = 0
            error_views = 0
            total_load_time = 0

            # Test connection and get views
            with server.auth.sign_in_with_personal_access_token(tableau_auth):
                all_views = list(TSC.Pager(server.views))

                for view in all_views:
                    try:
                        # Get view details and measure load time
                        view_start_time = datetime.now(UTC)
                        server.views.populate_preview_image(view)
                        server.views.populate_image(view)
                        view_end_time = datetime.now(UTC)

                        load_time = (view_end_time - view_start_time).total_seconds()
                        total_load_time += load_time

                        status = "normal"
                        if load_time > config['threshold']:
                            status = "slow"
                            slow_views += 1

                        views_data.append({
                            "name": view.name,
                            "id": view.id,
                            "status": status,
                            "load_time": f"{load_time:.2f}s",
                            "created_at": view.created_at.strftime('%Y-%m-%d %H:%M:%S') if view.created_at else None,
                            "updated_at": view.updated_at.strftime('%Y-%m-%d %H:%M:%S') if view.updated_at else None,
                            "project_name": view.project_name if hasattr(view, 'project_name') else None
                        })
                    except Exception as e:
                        error_views += 1
                        views_data.append({
                            "name": view.name,
                            "id": view.id,
                            "status": "error",
                            "error": str(e)
                        })

                end_time = datetime.now(UTC)
                check_duration = (end_time - start_time).total_seconds()
                avg_load_time = total_load_time / len(all_views) if all_views else 0

                response_data = {
                    "success": True,
                    "timestamp": end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    "user": "cod-emminex",
                    "total_views": len(all_views),
                    "server_url": config['server_url'],
                    "site_name": config['site_name'],
                    "views": views_data,
                    "status": "warning" if (slow_views > 0 or error_views > 0) else "success",
                    "slow_views": slow_views,
                    "error_views": error_views,
                    "avg_load_time": f"{avg_load_time:.2f}s",
                    "threshold": config['threshold'],
                    "check_duration": f"{check_duration:.2f}s",
                    "message": f"Monitored {len(all_views)} views. Found {slow_views} slow views and {error_views} errors."
                }

                # Send detailed webhook
                self.send_webhook("check", response_data)

                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, indent=2).encode())

        except Exception as e:
            error_data = {
                "success": False,
                "timestamp": datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S'),
                "user": "cod-emminex",
                "status": "error",
                "message": f"Error monitoring Tableau: {str(e)}",
                "error": str(e)
            }

            # Send error webhook
            self.send_webhook("error", error_data)

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
