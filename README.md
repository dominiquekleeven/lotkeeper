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

---

This project is archived and open-sourced as a reference implementation of a modern full-stack application with real-time data processing.
