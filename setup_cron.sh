#!/bin/bash

(crontab -l 2>/dev/null; echo "*/5 * * * * curl -s https://hng12-stage3-tableau-dashboard-monitor.onrender.com/ > /dev/null") | crontab -
