#!/bin/bash
# Automatic setup script for Polish Language Bot on PythonAnywhere

set -e  # Exit on any error

echo "🚀 Starting Polish Language Bot setup..."

# Get current username automatically
USERNAME=$(whoami)

# Check if we're in polish_bot directory, if not create and enter it
if [ ! -d ~/polish_bot ]; then
    echo "📁 Creating polish_bot directory..."
    mkdir -p ~/polish_bot
fi

cd ~/polish_bot

# Clone repository
echo "📥 Cloning repository from GitHub..."
if [ -d ".git" ]; then
    echo "Repository already exists, pulling latest changes..."
    git pull
else
    git clone https://github.com/Fastkiller333/polish-language-bot.git .
fi

# Create .env file with token
echo "🔑 Creating .env file with bot token..."
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=8234558544:AAFfcCb1tkdWG7btg4jZIIzjky3PiRF1qGw
EOF

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Print success message
echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Test the bot by running:"
echo "   cd ~/polish_bot && source venv/bin/activate && python main.py"
echo ""
echo "2. Set up a Scheduled Task on PythonAnywhere:"
echo "   Command: /home/$USERNAME/polish_bot/venv/bin/python /home/$USERNAME/polish_bot/main.py"
echo ""
echo "3. Or keep the bot running with:"
echo "   cd ~/polish_bot && source venv/bin/activate && nohup python main.py &"
echo ""

