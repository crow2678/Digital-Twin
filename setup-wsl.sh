#!/bin/bash
# Quick WSL Setup Script for Digital Twin Development
# Run this in WSL to get everything installed fast

echo "🚀 QUICK WSL SETUP FOR DIGITAL TWIN"
echo "=================================="
echo "📋 You already know what you need - this just installs it in WSL!"

# Update system
echo "📦 Updating WSL Ubuntu..."
sudo apt update && sudo apt upgrade -y

# Install Node.js (latest LTS) - Much faster than Windows installer
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
echo "✅ Node.js installed: $(node --version)"
echo "✅ NPM installed: $(npm --version)"

# Install Python (usually pre-installed, but ensure pip)
echo "📦 Setting up Python..."
sudo apt install -y python3-pip python3-venv
echo "✅ Python installed: $(python3 --version)"
echo "✅ Pip installed: $(pip3 --version)"

# Install your specific Python packages (copy from your Windows requirements)
echo "📦 Installing Python packages for Digital Twin..."
pip3 install \
    azure-search-documents \
    azure-core \
    langchain-openai \
    langchain-community \
    python-dotenv \
    fastapi \
    uvicorn \
    pydantic \
    azure-identity

echo "✅ Python packages installed!"

# Install Claude Code (the reason we're here!)
echo "📦 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code
echo "✅ Claude Code installed!"

# Create convenient aliases and shortcuts
echo "🔧 Setting up convenient shortcuts..."
cat >> ~/.bashrc << 'EOF'

# Digital Twin Development Shortcuts
alias twin='cd ~/digital-twin'
alias twin-api='cd ~/digital-twin && python3 behavioral_api_server.py'
alias twin-test='cd ~/digital-twin && python3 quick_system_test.py'
alias twin-memory='cd ~/digital-twin && python3 memory_inspector.py'
alias code-twin='cd ~/digital-twin && claude-code'

# Quick environment check
alias twin-status='echo "🔍 Digital Twin Environment Status:" && echo "Node: $(node --version)" && echo "Python: $(python3 --version)" && echo "Claude Code: $(claude-code --version 2>/dev/null || echo "Not found")"'

EOF

# Link to your Windows project folder
echo "🔗 Creating link to your Windows project..."
ln -sf /mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin ~/digital-twin

# Copy environment file
echo "📋 Copying environment configuration..."
if [ -f "/mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin/.env" ]; then
    cp /mnt/c/Tavant/Tavant/02_Paresh/Fun/digital-twin/.env ~/digital-twin/
    echo "✅ Environment file copied"
else
    echo "⚠️ Create .env file manually or copy from Windows"
fi

# Test installations
echo ""
echo "🧪 TESTING INSTALLATIONS..."
echo "=========================="
echo "Node.js: $(node --version)"
echo "NPM: $(npm --version)"
echo "Python: $(python3 --version)"
echo "Pip: $(pip3 --version)"

echo ""
echo "🧪 Testing Claude Code..."
if claude-code --version > /dev/null 2>&1; then
    echo "✅ Claude Code: $(claude-code --version)"
else
    echo "❌ Claude Code: Installation failed"
fi

echo ""
echo "🧪 Testing Python packages..."
python3 -c "
try:
    import azure.search.documents
    import langchain_openai
    import fastapi
    print('✅ All Python packages working!')
except ImportError as e:
    print(f'❌ Package import error: {e}')
"

echo ""
echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "📁 Your project is linked at: ~/digital-twin"
echo ""
echo "🚀 Quick start commands:"
echo "  twin              # Go to project folder"
echo "  twin-status       # Check environment"
echo "  twin-test         # Test digital twin system"
echo "  code-twin         # Start Claude Code"
echo ""
echo "💡 Reload your shell: source ~/.bashrc"
echo ""
echo "🎯 Next steps:"
echo "1. cd ~/digital-twin"
echo "2. source ~/.bashrc"
echo "3. twin-status"
echo "4. claude-code"