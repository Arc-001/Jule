#!/bin/bash

# Jule Bot Startup Script


if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
    fi
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment already activated."
fi

echo "Installing dependencies..."
pip install -r requirements.txt


#start jule bot in background
echo "Starting Jule Bot..."
cd src
coproc python3 bot.py >> bot.log 2>&1 &
cd ..
#sleep so that the db is made
sleep 5

#starting dashboard
echo "Starting Jule Bot Dashboard..."
coproc python3 dashboard.py >> dashboard.log 2>&1 &

echo "Jule Bot and Dashboard started successfully."