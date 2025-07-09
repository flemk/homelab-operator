#!/bin/bash
curl -s http://localhost:8000/cron/${API_KEY}/ || echo "Cron call failed at $(date)"
