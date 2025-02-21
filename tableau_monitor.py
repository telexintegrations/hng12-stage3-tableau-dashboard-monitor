import os
import json
import requests
import tableauserverclient as TSC
from datetime import datetime, timedelta
from dotenv import load_dotenv

class TableauMonitor:
    def __init__(self):
        load_dotenv()
        self.webhook_url = os.getenv("TELEX_WEBHOOK_URL")
        self.server_host = os.getenv("TABLEAU_SERVER_HOST")
        self.api_token = os.getenv("TABLEAU_API_TOKEN")
        self.site_name = os.getenv("TABLEAU_SITE_NAME", "")
        self.load_threshold = int(os.getenv("LOAD_TIME_THRESHOLD", 10))

        # Initialize Tableau Server Client
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name='MonitoringToken',
            personal_access_token=self.api_token,
            site_id=self.site_name
        )
        self.server = TSC.Server(self.server_host)
        self.server.auth = tableau_auth

    def get_slow_loading_dashboards(self):
        """Get dashboards that exceed the load time threshold"""
        slow_dashboards = []

        with self.server.auth.sign_in():
            all_views = list(TSC.Pager(self.server.views))

            for view in all_views:
                load_time = self.check_view_load_time(view)
                if load_time > self.load_threshold:
                    slow_dashboards.append({
                        'name': view.name,
                        'project': view.project_name,
                        'load_time': load_time,
                        'url': view.content_url
                    })

        return slow_dashboards

    def check_view_load_time(self, view):
        """Check the load time for a specific view"""
        try:
            start_time = datetime.now()
            self.server.views.populate_image(view)
            end_time = datetime.now()
            return (end_time - start_time).total_seconds()
        except Exception as e:
            print(f"Error checking view {view.name}: {str(e)}")
            return float('inf')

    def get_error_logs(self):
        """Get relevant error logs from Tableau Server"""
        errors = []

        with self.server.auth.sign_in():
            logs = self.server.log.get()
            for log in logs:
                if 'error' in log.lower() or 'failed' in log.lower():
                    errors.append(log)

        return errors

    def format_report(self, slow_dashboards, errors):
        """Format the monitoring report"""
        report = "🔍 Tableau Dashboard Performance Report\n\n"

        if slow_dashboards:
            report += "📊 Slow Loading Dashboards:\n"
            for dash in slow_dashboards:
                report += (
                    f"- {dash['name']} (Project: {dash['project']})\n"
                    f"  Load Time: {dash['load_time']:.2f}s\n"
                    f"  URL: {dash['url']}\n"
                )

        if errors:
            report += "\n⚠️ Recent Errors:\n"
            for error in errors[:5]:  # Show only last 5 errors
                report += f"- {error}\n"

        if not slow_dashboards and not errors:
            report += "✅ All dashboards are performing normally."

        return report

    def send_to_telex(self, report):
        """Send the report to Telex"""
        if not self.webhook_url:
            raise Exception("Telex webhook URL is not configured")

        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": report,
            "type": "tableau_monitoring"
        }

        response = requests.post(self.webhook_url, json=payload)
        response.raise_for_status()
        return response.status_code == 200

    def run(self):
        """Main execution method"""
        try:
            slow_dashboards = self.get_slow_loading_dashboards()
            errors = self.get_error_logs()

            if slow_dashboards or errors:
                report = self.format_report(slow_dashboards, errors)
                self.send_to_telex(report)
                print(f"Monitoring report sent successfully! Found {len(slow_dashboards)} slow dashboards and {len(errors)} errors.")
            else:
                print("No issues detected.")

        except Exception as e:
            error_msg = f"❌ Monitoring Error: {str(e)}"
            self.send_to_telex(error_msg)
            raise

if __name__ == "__main__":
    monitor = TableauMonitor()
    monitor.run()
