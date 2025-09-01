#!/bin/bash

echo "🧹 Cleaning up any existing Chrome processes..."
pkill -f chrome 2>/dev/null || true
pkill -f chromedriver 2>/dev/null || true

echo "🗑️  Removing old temp directories..."
rm -rf /tmp/wetex_chrome_* 2>/dev/null || true

echo "🚀 Starting scraper..."
python wetex_scraper.py

echo "✅ Done!"