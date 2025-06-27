#!/usr/bin/env python3
"""
Whisper Service Installer and Starter
Automatically installs requirements and starts the Whisper service
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    packages = [
        "openai-whisper",
        "fastapi",
        "uvicorn[standard]", 
        "python-multipart"
    ]
    
    print("🔧 Installing Whisper service requirements...")
    for package in packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All requirements installed successfully!")
    return True

def start_whisper_service():
    """Start the Whisper service"""
    print("\n🚀 Starting Whisper Service...")
    print("🌐 Service will be available at: http://localhost:8001")
    print("📖 API documentation at: http://localhost:8001/docs")
    print("🔍 Health check: http://localhost:8001/health")
    print("\nPress Ctrl+C to stop the service\n")
    
    try:
        # Start the service
        subprocess.run([sys.executable, "simple_whisper_service.py"])
    except KeyboardInterrupt:
        print("\n🛑 Whisper service stopped")
    except Exception as e:
        print(f"❌ Error starting service: {e}")

def main():
    print("🎙️ Whisper Service Setup for Digital Twin")
    print("=" * 50)
    
    # Check if requirements are already installed
    try:
        import whisper
        import fastapi
        import uvicorn
        print("✅ Requirements already installed")
        start_whisper_service()
    except ImportError:
        print("📋 Installing requirements first...")
        if install_requirements():
            start_whisper_service()
        else:
            print("❌ Failed to install requirements. Please install manually:")
            print("   pip install openai-whisper fastapi uvicorn python-multipart")

if __name__ == "__main__":
    main()