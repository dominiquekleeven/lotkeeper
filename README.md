
> This project is archived and open-sourced as a reference implementation of a modern full-stack application with real-time data processing focused on WoW auction house data.

# Lotkeeper

A comprehensive auction house data and statistics service for World of Warcraft private servers. Collects, analyzes, and visualizes auction house data to provide players with market insights and price trends.

## What it does

- Tracks auction house activity across multiple WoW private servers and realms
- Provides real-time auction data collection via authenticated agents
- Displays historical price tracking and market trend analysis
- Offers an interactive web dashboard with charts and statistics
- Exposes a RESTful API for programmatic access to auction data

## Tech Stack

**Backend**: FastAPI, SQLAlchemy, TimescaleDB (PostgreSQL), Redis/Valkey, Alembic  
**Frontend**: Vue 3, TypeScript, ECharts, Pico CSS  
**Infrastructure**: Docker Compose, Caddy reverse proxy


## Screenshots

**Homepage**
<img width="1920" height="1436" alt="image" src="https://github.com/user-attachments/assets/834b0293-9af8-480b-9d95-128085a7c93b" />

**Auction House page**
<img width="1920" height="1489" alt="image" src="https://github.com/user-attachments/assets/c9e267a4-da0c-41ad-930c-2fb12b06e4bf" />

**Search page**
<img width="1920" height="1436" alt="image" src="https://github.com/user-attachments/assets/1ee7f093-920d-464b-885d-54a2fd15932a" />

**Item details page**
<img width="1920" height="1907" alt="image" src="https://github.com/user-attachments/assets/637ea9c4-b277-4505-9cef-2488a3c11485" />


## Quick Start

### Development
```bash
# Start services
docker compose -f docker/dev.yml up -d postgres valkey

# Backend
uv sync
uv run alembic upgrade head
uv run python -m lotkeeper.main

# Frontend
cd frontend && npm install && npm run dev
```

### Production
```bash
docker compose -f deployment/prod.yml up -d
```

## Key Features

- Multi-server support with automatic realm creation
- Data validation and integrity checks
- Rate limiting and agent authentication
- Time-series data optimization with TimescaleDB
- Interactive charts and market analytics
- Advanced filtering and search capabilities

## API

Full API documentation available at `/api/docs` when running the application.

## Configuration

Set environment variables for database, cache, and security settings. See the Docker Compose files for examples.
