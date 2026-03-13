#!/bin/bash
cd "$(dirname "$0")"

echo "--- Bus Tracker Launcher ---"
# Install requirements if not present
pip3 install flask requests beautifulsoup4 --quiet

# Start the python app in the background
python3 app.py & 

# Wait 3 seconds for server to boot then open browser
sleep 3
open http://127.0.0.1:8000

echo "Server is running. Close this terminal to stop."
# Keep terminal open so the process doesn't die immediately
wait