@echo off
echo 🎙️ Starting Whisper Service for Digital Twin
echo ============================================
echo.

echo 📋 Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo.
echo 🔧 Installing Whisper service requirements...
pip install openai-whisper fastapi uvicorn[standard] python-multipart

echo.
echo 🚀 Starting Whisper Service...
echo 🌐 Service will be available at: http://localhost:8001
echo 📖 API docs at: http://localhost:8001/docs
echo.
echo Press Ctrl+C to stop the service
echo.

python simple_whisper_service.py

pause