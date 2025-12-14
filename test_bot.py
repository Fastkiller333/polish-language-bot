#!/usr/bin/env python3
"""
Test script to verify bot setup on PythonAnywhere
"""

import os
import sys

# Get script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"✓ Script directory: {BASE_DIR}")

# Check if .env exists
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    print(f"✓ .env file found")
else:
    print(f"✗ .env file NOT found at {env_path}")
    sys.exit(1)

# Check if words_database.json exists
words_path = os.path.join(BASE_DIR, 'words_database.json')
if os.path.exists(words_path):
    print(f"✓ words_database.json found")
else:
    print(f"✗ words_database.json NOT found at {words_path}")
    sys.exit(1)

# Check if database.py exists
db_module_path = os.path.join(BASE_DIR, 'database.py')
if os.path.exists(db_module_path):
    print(f"✓ database.py found")
else:
    print(f"✗ database.py NOT found at {db_module_path}")
    sys.exit(1)

# Try to import required modules
print("\nChecking Python packages...")

try:
    import telegram
    print(f"✓ python-telegram-bot installed (version {telegram.__version__})")
except ImportError as e:
    print(f"✗ python-telegram-bot NOT installed: {e}")
    sys.exit(1)

try:
    import apscheduler
    print(f"✓ apscheduler installed")
except ImportError as e:
    print(f"✗ apscheduler NOT installed: {e}")
    sys.exit(1)

try:
    import dotenv
    print(f"✓ python-dotenv installed")
except ImportError as e:
    print(f"✗ python-dotenv NOT installed: {e}")
    sys.exit(1)

try:
    import pytz
    print(f"✓ pytz installed")
except ImportError as e:
    print(f"✗ pytz NOT installed: {e}")
    sys.exit(1)

# Try to load .env and check token
print("\nChecking configuration...")
from dotenv import load_dotenv
load_dotenv(env_path)

token = os.getenv('TELEGRAM_BOT_TOKEN')
if token:
    print(f"✓ TELEGRAM_BOT_TOKEN found (length: {len(token)} chars)")
else:
    print(f"✗ TELEGRAM_BOT_TOKEN not found in .env")
    sys.exit(1)

# Try to import database module
print("\nTesting local imports...")
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from database import Database
    print(f"✓ Database module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Database: {e}")
    sys.exit(1)

# Try to initialize database
try:
    db_path = os.path.join(BASE_DIR, 'polish_bot.db')
    db = Database(db_path)
    print(f"✓ Database initialized at {db_path}")
except Exception as e:
    print(f"✗ Failed to initialize database: {e}")
    sys.exit(1)

# Try to load words database
try:
    with open(words_path, 'r', encoding='utf-8') as f:
        import json
        words = json.load(f)
    print(f"✓ Words database loaded ({len(words)} words)")
except Exception as e:
    print(f"✗ Failed to load words database: {e}")
    sys.exit(1)

print("\n" + "="*50)
print("✅ ALL CHECKS PASSED!")
print("="*50)
print("\nYour bot is ready to run with:")
print(f"  python3 {os.path.join(BASE_DIR, 'main.py')}")




