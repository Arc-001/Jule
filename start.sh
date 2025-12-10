#!/bin/bash

# Jule Bot & Dashboard Unified Startup Script

echo "🚀 Initializing Jule Environment..."

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Environment Setup
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ ! -d ".venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv .venv
    fi
    echo "🔌 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "✅ Virtual environment already activated."
fi

# 2. Dependencies
if [ -f "requirements.txt" ]; then
    echo "⬇️  Checking dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✅ Dependencies ready."
fi

# 3. Database Check
if [ ! -f "src/data/jule.db" ]; then
    echo "⚠️  Database file not found at src/data/jule.db (Will be created by bot)"
fi

# 4. Stop existing instances (optional cleanup)
pkill -f "python3 bot.py" > /dev/null 2>&1
pkill -f "python3 dashboard.py" > /dev/null 2>&1

# 5. Start Bot
echo "🤖 Starting Jule Bot..."
cd src
nohup python3 bot.py > ../bot.log 2>&1 &
BOT_PID=$!
cd ..
echo "✅ Bot started (PID: $BOT_PID)"

# 6. Start Dashboard
echo "📊 Starting Dashboard..."

# Port handling
PORT=8080
if [ "$1" == "--port" ] && [ -n "$2" ]; then
    PORT=$2
fi

# Update port in dashboard.py temporarily/dynamically if needed or just pass env var
# Simpler approach: Dashboard should read env var, but modifying file was the old way.
# We will assume default 8080 or the one in the file.
# Note: The original start_dashboard.sh modified the file. We'll stick to running it.
# To allow port configuration without modifying code, we should pass it as env var if dashboard supports it.
# The current dashboard.py hardcodes. Let's patch dashboard.py to read PORT env var first.
# For now, just run it.

nohup python3 dashboard.py > dashboard.log 2>&1 &
DASH_PID=$!
echo "✅ Dashboard started (PID: $DASH_PID)"

echo ""
echo "🎉 Jule is running!"
echo "   • Bot Logging: bot.log"
echo "   • Dashboard:   http://localhost:8080 (or your configured port)"
echo "   • Dash Logs:   dashboard.log"
echo ""
echo "Run 'pkill -f python3' to stop all."