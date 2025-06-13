# README.md

# TailingsIQ Backend API

This repository contains the backend API for the TailingsIQ application, providing endpoints for Query Assistant, Risk Assessment, Monitoring, and Knowledge Management.

## Features

- **Query Assistant**: AI-powered interface for tailings management questions
- **Risk Assessment**: Comprehensive risk evaluation tools
- **Monitoring**: Real-time data and alert management
- **Knowledge Management**: Document repository and management

## Deployment Options

This package includes configuration for multiple deployment methods:

1. **Docker** - Using Dockerfile (Recommended)
2. **Railway/Heroku** - Using Procfile
3. **Python Package** - Using pyproject.toml

For detailed deployment instructions, please refer to the `DEPLOYMENT_GUIDE.md` file.

## Requirements

- Python 3.8+
- FastAPI
- Uvicorn
- PyJWT
- Python-Jose
- Python-Multipart
- Pydantic

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   uvicorn main:app --reload
   ```

3. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## License

Proprietary - All rights reserved
