#!/bin/bash
# Simple installation script for PythonAnywhere
# Installs packages globally (user scope) so you can use: python3 main.py

set -e

echo "🚀 Installing Polish Language Bot..."

# Navigate to bot directory
cd ~/polish_bot || { mkdir -p ~/polish_bot && cd ~/polish_bot; }

# Remove old virtual environment if exists
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Clone or update repository
if [ -d ".git" ]; then
    echo "📥 Updating repository..."
    git pull
else
    echo "📥 Cloning repository..."
    git clone https://github.com/Fastkiller333/polish-language-bot.git .
fi

# Create .env file template
echo "🔑 Creating .env file template..."
if [ ! -f .env ]; then
    cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
EOF
    echo "⚠️  ВАЖНО: Откройте файл .env и замените YOUR_BOT_TOKEN_HERE на ваш настоящий токен от @BotFather"
else
    echo "✓ .env уже существует, пропускаем..."
fi

# Install packages globally (user scope)
echo "📦 Installing dependencies globally..."
python3 -m pip install --user -r requirements.txt

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 FIRST: Test that everything works:"
echo "   python3 ~/polish_bot/test_bot.py"
echo ""
echo "📋 If test passes, run the bot manually:"
echo "   python3 ~/polish_bot/main.py"
echo ""
echo "📋 For Always-on Task on PythonAnywhere:"
echo "   Command: python3 /home/$USERNAME/polish_bot/main.py"
echo "   Working directory: (leave empty)"
echo ""
echo "⚠️  Для информации о безопасности читайте: SECURITY.md"
echo ""

