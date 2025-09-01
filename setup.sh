#!/bin/bash

# Setup script for WETEX Selenium Scraper in GitHub Codespaces
# Run this script to install all dependencies

echo "🚀 Setting up WETEX Scraper environment..."
echo "========================================="

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install Chrome browser
echo "🌐 Installing Google Chrome..."
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# Install required system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y \
    wget \
    unzip \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    libpango1.0-0 \
    libgbm1

# Get Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "✓ Chrome version: $CHROME_VERSION"

# Install ChromeDriver
echo "🚗 Installing ChromeDriver..."
# Get the major version number
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)

# Download matching ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION")
wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

echo "✓ ChromeDriver version: $CHROMEDRIVER_VERSION"

# Install Python packages
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install selenium beautifulsoup4 pandas requests

# Create requirements.txt
echo "📝 Creating requirements.txt..."
cat > requirements.txt << EOF
selenium==4.17.2
beautifulsoup4==4.12.3
pandas==2.1.4
requests==2.31.0
EOF

echo "✓ Requirements file created"

# Test Chrome installation
echo "🧪 Testing Chrome installation..."
google-chrome --version
chromedriver --version

echo ""
echo "✅ Setup completed successfully!"
echo "========================================="
echo "You can now run the scraper with:"
echo "  python wetex_scraper.py"
echo ""
echo "Note: The scraper is set to run in headless mode by default."
echo "This is perfect for GitHub Codespaces!"
