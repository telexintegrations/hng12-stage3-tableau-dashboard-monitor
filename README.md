# Tableau Dashboard Monitor for Telex

A Telex integration that monitors Tableau dashboards for performance issues and failures. The integration checks dashboard load times and availability at specified intervals and reports issues to your Telex channel.

![Tableau Monitor Logo](https://img.icons8.com/color/48/tableau-software.png)

## Features

-  Real-time dashboard load time monitoring
-  Automatic failure detection
-  Performance threshold alerts
-  Error log analysis
-  Configurable check intervals using cron syntax
-  Automatic status reporting to Telex

## Screenshots

![Telex Integration Example](https://github.com/telexintegrations/hng12-stage3-tableau-dashboard-monitor/blob/main/Capture.PNG)

Example alerts in Telex channel:
```
Tableau Monitor Check - 2025-02-23 02:44:40
Server: https://dub01.online.tableau.com
Site: emminexy-f537b42aad
Total Views: 17
Active Views: 15
Error Views: 2

Views Status:
1. Sales Dashboard (Main Project) - ACTIVE
2. Performance Overview (Analytics) - ACTIVE
3. Error Report (Finance) - ERROR
```

## Setup

### Prerequisites

- Python 3.9+
- Tableau Server access
- Tableau API token
- Telex webhook URL

### Environment Variables

```bash
TABLEAU_SERVER_HOST=your-tableau-server
TABLEAU_SITE_NAME=your-site-name
TABLEAU_TOKEN_NAME=your-token-name
TABLEAU_API_TOKEN=your-api-token
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/telexintegrations/hng12-stage3-tableau-dashboard-monitor/
cd hng12-stage3-tableau-dashboard-monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run locally:
```bash
python -m flask run
```

### Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure environment variables
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn "api.monitor:app"`

## API Endpoints

### Integration Configuration
```http
GET /api/integration
```
Returns the Telex integration configuration.

### Monitor Status
```http
GET /api/monitor
```
Manually triggers a dashboard check.

```http
POST /api/monitor
```
Receives tick requests from Telex for scheduled checks.

## Telex Integration

1. Add the integration URL to your Telex organization:
```
https://hng12-stage3-tableau-dashboard-monitor.onrender.com/api/integration
```

2. Configure settings:
   - `interval`: Cron expression for check frequency (to set 10 mins: `*/10 * * * *`)
   - `Load Time Threshold`: Maximum acceptable load time in seconds (default: `10`)

## Testing

Run tests:
```bash
pytest
```

## Development

Current development status:
- Version: 1.0.0
- Last Updated: 2025-02-23 02:44:40
- Developer: cod-emminex

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support:
1. Open an issue
2. Contact via Telex: emminexy@yahoo.com
3. GitHub: [https://github.com/cod-emminex]

## Acknowledgments

- Tableau Server Client library
- Telex platform
- Icons by Icons8
