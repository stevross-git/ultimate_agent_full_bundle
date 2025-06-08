@echo off

echo 🔧 Setting up virtual environment...

REM Create virtual environment
python -m venv venv

REM Activate environment
venv\Scripts\activate

echo 📦 Installing dependencies...
python.exe -m pip install --upgrade pip
pip install --upgrade pip
pip install -r requirements.txt

echo 🚀 Running the Enhanced Node Server...
python main.py
