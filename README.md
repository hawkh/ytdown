# YouTube Video Downloader 🎥

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-streamlit-app-url.streamlit.app/)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A Streamlit web application for downloading YouTube videos in various resolutions. Effortlessly save videos in your preferred quality (144p to 1080p) with real-time progress tracking.

## Features ✨
- Multi-quality support (144p, 360p, 720p, 1080p)
- Progress bar with download speed indicator
- Video preview after download
- Direct download button for saved files
- Error handling and troubleshooting guide

## Installation 🛠️

### Prerequisites
- Python 3.8+
- FFmpeg (installed automatically in setup)

### Local Setup
```bash
# Clone repository
git clone https://github.com/your-username/ytdown.git
cd ytdown

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install system dependencies (FFmpeg)
chmod +x setup.sh
./setup.sh

# Run application
streamlit run main.py
