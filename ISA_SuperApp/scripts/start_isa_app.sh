#!/bin/bash

# Define the absolute path to the project root directory
PROJECT_ROOT="/Users/frisowempe/Desktop/ISA_B/2-main/ISA_SuperDesign_VSCode_Copilot_OneShot_2025-08-17"

# Navigate to the project root
cd "$PROJECT_ROOT" || { echo "Error: Could not change to project directory."; exit 1; }

# Activate the Python virtual environment
source .venv/bin/activate || { echo "Error: Could not activate virtual environment. Make sure .venv exists and is set up correctly."; exit 1; }

# Start the FastAPI server in the background
# Redirect stdout and stderr to a log file in the parent directory of the project root
echo "Starting FastAPI server..."
uvicorn src.api_server:app --reload --port 8787 > ../fastapi_server.log 2>&1 &
FASTAPI_PID=$!
echo "FastAPI server started with PID: $FASTAPI_PID. Logs in ../fastapi_server.log"

# Wait a moment for the server to start
sleep 5

# Launch the Electron application
echo "Launching Electron application..."
open "desktop/electron/dist/mac-universal/ISA-SuperDesign-Unsigned.app"

echo "Application launched. You can close this terminal."
echo "To stop the FastAPI server, find its process (PID: $FASTAPI_PID) and kill it using: kill $FASTAPI_PID"
