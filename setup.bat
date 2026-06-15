@echo off
echo Setting up YouTube Metadata Bot...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo.
echo Setup complete! 
echo Make sure you have copied .env.example to .env and filled in your API keys.
echo Make sure you have downloaded client_secret.json from Google Cloud Console.
echo.
echo To run the bot, just run: run_bot.bat
echo.
pause
