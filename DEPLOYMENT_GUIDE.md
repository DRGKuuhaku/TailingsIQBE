# TailingsIQ Backend Deployment Guide

## Overview

This guide provides instructions for deploying the TailingsIQ backend API using multiple deployment methods. The backend is built with FastAPI and includes modules for Query Assistant, Risk Assessment, Monitoring, and Knowledge Management.

## Deployment Options

This package includes configuration for three deployment methods:
1. **Railway/Heroku** - Using Procfile
2. **Docker** - Using Dockerfile
3. **Python Package** - Using pyproject.toml

## Option 1: Docker Deployment (Recommended)

### Step 1: Push code to GitHub
1. Push all files from this package to your GitHub repository
2. Ensure your repository includes the `Dockerfile`

### Step 2: Deploy to Railway
1. Log in to your Railway account at [railway.app](https://railway.app)
2. Create a new project:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub account if not already connected
   - Select your backend repository
   - In the deployment settings, select "Docker" as the deployment method

3. Railway will automatically detect the Dockerfile and build your container

4. Verify the deployment:
   - Once deployed, Railway will provide a URL for your API
   - Test the API by accessing the root endpoint

## Option 2: Railway with Procfile

### Step 1: Push code to GitHub
1. Push all files from this package to your GitHub repository
2. Ensure your repository includes the `Procfile`

### Step 2: Deploy to Railway
1. Log in to your Railway account
2. Create a new project and select your repository
3. Railway will detect the Procfile and use it to run your application

## Option 3: Python Package Deployment

1. Install as a package:
   ```bash
   pip install -e .
   ```

2. Run the application:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**:
   - Ensure all dependencies are listed in `requirements.txt`
   - Try using the Docker deployment method which explicitly installs dependencies

2. **CORS Issues**:
   - Verify that your CORS middleware is configured correctly in `main.py`
   - Ensure the frontend origin is allowed in the CORS configuration

## Security Considerations

1. Replace the placeholder `SECRET_KEY` in main.py with a secure random string
2. In production, restrict CORS to specific origins
3. Use environment variables for sensitive configuration
