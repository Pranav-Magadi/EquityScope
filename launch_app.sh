#!/bin/bash

# Navigate to the EquityScope directory
cd /Users/pnm2/Desktop/CodingProjects/EquityScope

# Stop any existing processes
echo "🛑 Stopping any existing processes..."
./stop_development.sh

# Wait a moment for processes to stop
sleep 2

# Start the application
echo "🚀 Starting EquityScope application..."
./start_development.sh
