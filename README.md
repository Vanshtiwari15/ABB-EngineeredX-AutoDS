# AutoDS-LLM: Designing and Evaluating Adaptive Language Models for Evolving Data Science Workflows

AutoDS-LLM is a futuristic AI-powered AutoML platform that automates the complete machine learning workflow from dataset upload to model training, evaluation, and prediction.

Built using FastAPI, Machine Learning, and a modern AI SaaS dashboard UI.

---

# Project Overview

This platform allows users to:

- Upload datasets
- Automatically analyze data
- Detect ML task type
- Train multiple ML models
- Compare model performance
- Generate predictions
- Visualize metrics and analytics
- Download trained models and reports

The system reduces manual ML pipeline work and provides an end-to-end automated machine learning experience.

---

# Features

## AI Automated Workflow

- Automatic dataset profiling
- Automatic preprocessing
- Automatic task detection
- Automatic model selection
- Automatic training pipeline
- Automatic evaluation pipeline

---

## Supported ML Tasks

- Classification
- Regression
- Clustering

---

## Backend Features

- FastAPI REST APIs
- Structured modular architecture
- Logging system
- Model saving/loading
- Prediction APIs
- Metrics APIs
- Error handling
- Clean scalable backend

---

## Frontend Features

- Futuristic AI dashboard
- Dark modern UI
- Animated particles background
- GSAP animations
- Interactive analytics charts
- Drag and drop dataset upload
- Real-time training logs
- Responsive UI/UX
- Glassmorphism design

---

# Tech Stack

## Backend

- FastAPI
- Python
- Scikit-learn
- Pandas
- NumPy
- Joblib
- Uvicorn

---

## Frontend

- HTML5
- Tailwind CSS
- JavaScript ES6
- GSAP
- Chart.js
- tsParticles

---

# Project Architecture

```text
User Uploads Dataset
        ↓
Data Profiling
        ↓
Task Detection
        ↓
Model Training
        ↓
Model Evaluation
        ↓
Best Model Selection
        ↓
Prediction API
        ↓
Analytics & Reports
```

---

# Backend Structure

```text
backend/
│
├── agents/
├── api/
├── core/
├── models/
├── outputs/
├── services/
├── tests/
├── utils/
├── main.py
└── requirements.txt
```

---

# Frontend Structure

```text
frontend/
│
├── index.html
├── style.css
├── app.js
│
├── pages/
├── components/
└── assets/
```

---

# API Endpoints

## Upload Dataset

```http
POST /api/upload
```

Uploads dataset and starts profiling.

---

## Train Model

```http
POST /api/train
```

Automatically trains ML models.

---

## Predict

```http
POST /api/predict
```

Generates predictions using trained models.

---

## Metrics

```http
GET /api/metrics
```

Returns analytics and evaluation metrics.

---

# Installation

## Clone Repository

```bash
git clone https://github.com/Vanshtiwari15/ABB-EngineeredX-AutoDS.git
```

---

## Backend Setup

```bash
cd AutoDS-LLM
python -m venv .venv
```

Activate virtual environment:

### Windows

```bash
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

# Run Backend

```bash
uvicorn backend.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

# Run Frontend

Open:

```text
frontend/index.html
```

OR run using VS Code Live Server.

---

# Screenshots

## Dashboard

- AI analytics dashboard
- Model leaderboard
- Accuracy charts
- Upload interface

---

# Future Improvements

- LLM powered dataset understanding
- Auto feature engineering
- Explainable AI
- Docker deployment
- Cloud integration
- Multi-user support
- Real-time monitoring
- HuggingFace integration

---

# Use Cases

- Automated machine learning
- Rapid ML prototyping
- Educational ML platform
- Dataset analysis
- AI-powered analytics
- Recruiter/demo showcase project

---

# Highlights

- Full-stack AI project
- Production-style architecture
- Modern UI/UX
- End-to-end ML automation
- Real-world engineering workflow

---

# Author

## Vansh Tiwari

Engineering Student | Machine Learning Enthusiast

GitHub:
https://github.com/Vanshtiwari15

---

# License

This project is developed for educational and engineering purposes.
