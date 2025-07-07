#!/bin/bash\n\
# Internal cron script to call the homelab-operator cron endpoint\n\
API_KEY=${API_KEY:-DEFAULT_API_KEY}\n\
curl -s http://localhost:8000/cron/${API_KEY}/ || echo "Cron call failed at $(date)"
