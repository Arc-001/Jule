#!/bin/bash

# Jule Bot Dashboard Startup Script

echo "🚀 Starting Jule Bot Dashboard..."
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not activated"
    echo "Attempting to activate .venv..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ No .venv found. Please create a virtual environment first."
        exit 1
    fi
fi

# Check if database exists
if [ ! -f "src/data/jule.db" ]; then
    echo "⚠️  Database not found at src/data/jule.db"
    echo "The dashboard will start, but no data will be displayed until the bot creates the database."
    echo ""
fi

# Check if running as root (needed for port 80)
if [ "$EUID" -ne 0 ] && [ "$1" != "--port" ]; then
    echo "⚠️  Port 80 requires root privileges"
    echo ""
    echo "Options:"
    echo "  1. Run with sudo: sudo ./start_dashboard.sh"
    echo "  2. Use different port: ./start_dashboard.sh --port 8080"
    echo "  3. Grant capability: sudo setcap 'cap_net_bind_service=+ep' \$(which python3)"
    echo ""

    # Ask user what they want to do
    read -p "Run on port 8080 instead? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Modify dashboard.py temporarily to use port 8080
        echo "📝 Using port 8080..."
        python3 -c "
import sys
with open('dashboard.py', 'r') as f:
    code = f.read().replace('port=80', 'port=8080')
exec(code)
"
        exit 0
    else
        echo "❌ Cancelled. Please run with sudo or use --port flag."
        exit 1
    fi
fi

# Start the dashboard
echo "📊 Dashboard starting on http://localhost:80"
echo "Press Ctrl+C to stop"
echo ""

if [ "$1" = "--port" ]; then
    PORT=${2:-8080}
    echo "Using port $PORT"
    python3 -c "
with open('dashboard.py', 'r') as f:
    code = f.read().replace('port=80', 'port=$PORT')
exec(code)
"
else
    python3 dashboard.py
fi

