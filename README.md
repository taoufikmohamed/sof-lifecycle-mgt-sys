# Software Lifecycle Automation Project

## Overview
This project implements an automated software development lifecycle using AI agents to handle development, testing, and deployment tasks. It uses the Deepseek AI model for code generation and automation.

## Project Structure

. ├── deepseek/ # Core AI functionality ├── deploy/ # Deployment configurations ├── repository/ # Source code repository ├── .env # Environment variables ├── .gitignore # Git ignore rules ├── main.py # Main application entry ├── requirements.txt # Python dependencies └── software_lifecycle.py # Lifecycle management

## Features
- Automated code generation using Deepseek AI
- Automated testing suite
- Continuous deployment pipeline
- Project health monitoring
- Git repository management

## Prerequisites
- Python 3.11+
- Node.js (for deployment)
- Git
- Deepseek API key

## Installation
1. Clone the repository:
```bash

git clone <repository-url>
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

pip install -r requirements.txt

## Configure environment: Create .env file with:
DEEPSEEK_API_KEY=<your-api-key>
repo_url=<repository-url>

## Run the main application:
    python main.py

## Development
software_lifecycle.py contains the core agent classes
main.py orchestrates the lifecycle workflow
Tests are located in test_handle.py


