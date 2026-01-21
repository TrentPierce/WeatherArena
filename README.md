# WeatherArena Platform

A premium weather model ranking and visualization platform.

## Architecture

- **Frontend**: Next.js 16 (React), Tailwind CSS, Leaflet Maps
- **Backend**: FastAPI (Python), Herbie (GRIB2), Supabase (PostgreSQL)

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Supabase account (credentials in `.env`)

### Backend Setup

1. Navigate to backend:
   ```bash
   cd backend
   ```
2. Create venv and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```
   API will be at `http://localhost:8000`.

### Frontend Setup

1. Navigate to frontend:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run development server:
   ```bash
   npm run dev
   ```
   App will be at `http://localhost:3000`.

## Features
- Interactive Forecast Map (Leaflet)
- Model Verification Engine with Elo Rankings
- GRIB2 Data Ingestion (Herbie)
