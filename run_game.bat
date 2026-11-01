@echo off
cd /d "%~dp0"
set SDL_VIDEO_CENTERED=1
python launcher.py main.py
