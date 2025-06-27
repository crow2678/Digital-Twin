#!/usr/bin/env python3
"""
Setup script for Digital Twin Web Application
Installs dependencies and prepares the environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is too old. Need Python 3.8+")
        return False

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    directories = [
        "uploads",
        "results", 
        "logs",
        "static",
        "templates"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}/")
    
    print("✅ Directories created successfully")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Check if pip is available
    pip_commands = ["pip", "pip3", "py -m pip"]
    pip_cmd = None
    
    for cmd in pip_commands:
        if run_command(f"{cmd} --version", f"Checking {cmd}"):
            pip_cmd = cmd
            break
    
    if not pip_cmd:
        print("❌ No pip command found. Please install pip first.")
        return False
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        return run_command(
            f"{pip_cmd} install -r requirements.txt",
            "Installing requirements from requirements.txt"
        )
    else:
        # Install core dependencies manually
        core_deps = [
            "fastapi",
            "uvicorn[standard]",
            "python-multipart",
            "jinja2",
            "pydantic",
            "python-dotenv"
        ]
        
        success = True
        for dep in core_deps:
            if not run_command(f"{pip_cmd} install {dep}", f"Installing {dep}"):
                success = False
        
        return success

def check_env_file():
    """Check for .env file with Azure credentials"""
    print("🔧 Checking environment configuration...")
    
    env_file = Path("../.env")
    if env_file.exists():
        print("✅ Found .env file in parent directory")
        
        # Check for required variables
        with open(env_file, 'r') as f:
            content = f.read()
        
        required_vars = [
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_KEY", 
            "AZURE_SEARCH_INDEX",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if var not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
            print("   The application may not work correctly without these.")
        else:
            print("✅ All required environment variables found")
        
        return True
    else:
        print("⚠️ No .env file found")
        print("   Create a .env file with your Azure credentials")
        return False

def create_startup_script():
    """Create startup script for easy launching"""
    print("📝 Creating startup script...")
    
    if os.name == 'nt':  # Windows
        script_content = '''@echo off
echo Starting Digital Twin Web Application...
echo.
echo Access the application at: http://localhost:8080
echo Press Ctrl+C to stop the server
echo.
python app.py
pause
'''
        with open("start.bat", "w") as f:
            f.write(script_content)
        print("✅ Created start.bat for Windows")
    
    else:  # Unix/Linux/Mac
        script_content = '''#!/bin/bash
echo "Starting Digital Twin Web Application..."
echo ""
echo "Access the application at: http://localhost:8080"
echo "Press Ctrl+C to stop the server"
echo ""
python3 app.py
'''
        with open("start.sh", "w") as f:
            f.write(script_content)
        os.chmod("start.sh", 0o755)
        print("✅ Created start.sh for Unix/Linux/Mac")
    
    return True

def create_azure_deployment():
    """Create Azure deployment configuration"""
    print("☁️ Creating Azure deployment configuration...")
    
    # Azure Web App configuration
    app_yaml = '''# Azure App Service deployment configuration
runtime:
  name: python
  version: "3.10"

env_variables:
  WEBSITES_PORT: 8080
  
startup_command: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8080
'''
    
    with open("app.yaml", "w") as f:
        f.write(app_yaml)
    
    # Docker configuration for Azure Container Instances
    dockerfile = '''FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads results logs

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
'''
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    
    # Azure deployment script
    deploy_script = '''#!/bin/bash
# Azure deployment script for Digital Twin Web Application

echo "🚀 Deploying Digital Twin Web Application to Azure..."

# Set your Azure details here
RESOURCE_GROUP="digital-twin-rg"
APP_NAME="digital-twin-web"
LOCATION="eastus"

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login..."
az account show > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Please login to Azure:"
    az login
fi

# Create resource group if it doesn't exist
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service plan
echo "🖥️ Creating App Service plan..."
az appservice plan create --name ${APP_NAME}-plan --resource-group $RESOURCE_GROUP --sku B1 --is-linux

# Create Web App
echo "🌐 Creating Web App..."
az webapp create --resource-group $RESOURCE_GROUP --plan ${APP_NAME}-plan --name $APP_NAME --runtime "PYTHON|3.10"

# Deploy code
echo "📤 Deploying application..."
az webapp up --name $APP_NAME --resource-group $RESOURCE_GROUP --runtime "PYTHON:3.10"

# Set environment variables (you'll need to add your Azure credentials)
echo "🔧 Setting environment variables..."
echo "Please set your Azure credentials in the Azure portal:"
echo "- AZURE_SEARCH_ENDPOINT"
echo "- AZURE_SEARCH_KEY"
echo "- AZURE_SEARCH_INDEX"  
echo "- AZURE_OPENAI_ENDPOINT"
echo "- AZURE_OPENAI_KEY"

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://${APP_NAME}.azurewebsites.net"
'''
    
    with open("deploy_azure.sh", "w") as f:
        f.write(deploy_script)
    os.chmod("deploy_azure.sh", 0o755)
    
    print("✅ Created Azure deployment files:")
    print("   • app.yaml - Azure App Service configuration")
    print("   • Dockerfile - Container configuration")  
    print("   • deploy_azure.sh - Deployment script")
    
    return True

def main():
    """Main setup function"""
    print("🚀 DIGITAL TWIN WEB APPLICATION SETUP")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup directories
    if not setup_directories():
        print("❌ Failed to setup directories")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check environment
    check_env_file()
    
    # Create startup script
    if not create_startup_script():
        print("❌ Failed to create startup script")
    
    # Create Azure deployment config
    if not create_azure_deployment():
        print("❌ Failed to create Azure deployment config")
    
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    
    print("\n📋 Next Steps:")
    print("1. 🔧 Configure your .env file with Azure credentials")
    print("2. 🚀 Start the application:")
    
    if os.name == 'nt':
        print("   • Windows: Double-click start.bat or run 'python app.py'")
    else:
        print("   • Unix/Linux/Mac: Run './start.sh' or 'python3 app.py'")
    
    print("3. 🌐 Open http://localhost:8080 in your browser")
    print("4. ☁️ For Azure deployment: Run './deploy_azure.sh'")
    
    print("\n💡 Features Available:")
    print("   • Document analysis with drag & drop")
    print("   • Meeting transcript processing")
    print("   • Smart question generation")
    print("   • Email drafting assistance")
    print("   • Real-time progress tracking")
    print("   • Copy/export functionality")
    
    print("\n🎯 Ready to transform your productivity with AI!")

if __name__ == "__main__":
    main()