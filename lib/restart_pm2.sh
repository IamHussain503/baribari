#!/bin/bash

# Stop all PM2 processes
pm2 stop all

# Wait a bit for all processes to stop
sleep 5

# Restart all PM2 processes
pm2 restart all

echo "PM2 processes have been restarted."
