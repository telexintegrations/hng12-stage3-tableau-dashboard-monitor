#!/usr/bin/env python3

import os
import sys
import json
import time
import logging
from datetime import datetime, UTC
import requests
from dotenv import load_dotenv
import tableauserverclient as TSC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TableauMonitor')

class TableauMonitor:
    def __init__(self):
        load_dotenv()
        self.server_url = self._clean_server_url(os.getenv('TABLEAU_SERVER_HOST', 'https://dub01.online.tableau.com'))
        self.site_name = os.getenv('TABLEAU_SITE_NAME', 'emminexy-f537b42aad')
        self.token_name = os.getenv('TABLEAU_TOKEN_NAME', 'TelescopeMonitoring')
        self.token = os.getenv('TABLEAU_API_TOKEN')
        self.webhook_url = "https://ping.telex.im/v1/webhooks/019528ca-ae9c-79d7-a3ed-2dc5866df56a"
        self.threshold = int(os.getenv('LOAD_TIME_THRESHOLD', 10))

        if not all([self.server_url, self.site_name, self.token]):
            logger.error("Missing required environment variables")
            sys.exit(1)

    def _clean_server_url(self, url):
        """Clean the server URL to remove unnecessary parts"""
        if not url:
            return url
        if '/#/site/' in url:
            url = url.split('/#/site/')[0]
        return url.rstrip('/')

    def _send_webhook(self, event_name, status, message):
        """Send webhook notification to Telex"""
        payload = {
            "event_name": event_name,
            "username": "cod-emminex",
            "status": status,
            "message": message
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code != 202:
                logger.error(f"Webhook failed with status {response.status_code}: {response.text}")
            return response.status_code == 202
        except Exception as e:
            logger.error(f"Failed to send webhook: {str(e)}")
            return False

    def measure_load_time(self, server, view):
        """Measure the time it takes to load a view's data"""
        try:
            start_time = time.time()

            # Get view data
            server.views.populate_preview_image(view)
            server.views.populate_image(view)
            server.views.populate_pdf(view)

            end_time = time.time()
            load_time = end_time - start_time

            return load_time

        except Exception as e:
            logger.error(f"Error measuring load time for {view.name}: {str(e)}")
            return None

    def check_dashboards(self):
        """Monitor Tableau dashboards for performance issues"""
        try:
            # Initialize Tableau Server client
            tableau_auth = TSC.PersonalAccessTokenAuth(
                token_name=self.token_name,
                personal_access_token=self.token,
                site_id=self.site_name
            )

            server = TSC.Server(
                self.server_url,
                use_server_version=False,
                http_options={'verify': True}
            )
            server.version = '3.16'

            with server.auth.sign_in_with_personal_access_token(tableau_auth):
                # Get all views
                all_views = list(TSC.Pager(server.views))
                logger.info(f"Found {len(all_views)} views to monitor")

                slow_dashboards = []
                error_dashboards = []

                for view in all_views:
                    try:
                        load_time = self.measure_load_time(server, view)

                        if load_time is None:
                            error_dashboards.append(view.name)
                            continue

                        if load_time > self.threshold:
                            slow_dashboards.append((view.name, load_time))
                            message = (
                                f"Dashboard '{view.name}' is loading slowly. "
                                f"Load time: {load_time:.2f}s (threshold: {self.threshold}s)"
                            )
                            logger.warning(message)
                            self._send_webhook(
                                event_name="tableau_slow_dashboard",
                                status="warning",
                                message=message
                            )
                        else:
                            logger.info(f"Dashboard '{view.name}' load time OK: {load_time:.2f}s")

                    except Exception as e:
                        error_msg = f"Error monitoring dashboard '{view.name}': {str(e)}"
                        logger.error(error_msg)
                        error_dashboards.append(view.name)
                        self._send_webhook(
                            event_name="tableau_monitor_error",
                            status="error",
                            message=error_msg
                        )

                # Send summary
                summary = (
                    f"Monitoring Summary ({datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')})\n"
                    f"Total Dashboards: {len(all_views)}\n"
                    f"Slow Dashboards: {len(slow_dashboards)}\n"
                    f"Error Dashboards: {len(error_dashboards)}"
                )

                if slow_dashboards:
                    summary += "\n\nSlow Dashboards:"
                    for name, time in slow_dashboards:
                        summary += f"\n- {name}: {time:.2f}s"

                if error_dashboards:
                    summary += "\n\nDashboards with Errors:"
                    for name in error_dashboards:
                        summary += f"\n- {name}"

                self._send_webhook(
                    event_name="tableau_monitor_summary",
                    status="info",
                    message=summary
                )

        except Exception as e:
            error_msg = f"Failed to monitor Tableau dashboards: {str(e)}"
            logger.error(error_msg)
            self._send_webhook(
                event_name="tableau_monitor_error",
                status="error",
                message=error_msg
            )
            return False

        return True

def main():
    monitor = TableauMonitor()
    success = monitor.check_dashboards()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
