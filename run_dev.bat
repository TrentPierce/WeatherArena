@echo off
echo Starting WeatherArena Dev Environment...
start "WeatherArena Backend" cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --reload"
start "WeatherArena Frontend" cmd /k "cd frontend && npm run dev"
echo Services starting...
echo Frontend: http://localhost:3000
echo Backend: http://localhost:8000
