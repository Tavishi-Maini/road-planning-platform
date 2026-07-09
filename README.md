# 🛣️ AI Road Planning Platform

An AI-powered Road Construction Planning Platform that predicts key project metrics using Machine Learning and provides an interactive decision-support dashboard for planners, engineers, contractors, and government agencies.

Live Demo: https://road-planning-platform.streamlit.app/

---

## 📌 Overview

Road construction projects involve hundreds of technical, financial, environmental, and logistical parameters. Estimating project cost, duration, manpower, machinery, and material requirements manually is time-consuming and often inconsistent.

This platform leverages Machine Learning to assist engineers in making faster and more data-driven planning decisions.

The system predicts:

- 💰 Total Project Cost
- 📅 Construction Duration
- 🧱 Material Requirement Index
- 👷 Manpower Hours per Kilometer
- 🚜 Machinery Hours per Kilometer

through an intuitive Streamlit-based web interface.

---

# 🚀 Features

### 📊 Multi-Target Prediction

Predict five critical construction metrics simultaneously using independently optimized ML models.

---

### 📋 Project Information Management

- Create multiple road projects
- Store project metadata
- View historical predictions
- Compare different projects

---

### 🤖 Machine Learning Engine

The platform uses multiple optimized machine learning models.

| Target | Final Model |
|----------|-------------|
| Total Cost | CatBoost |
| Construction Duration | CatBoost |
| Material Index | CatBoost |
| Manpower Hours/km | ElasticNet |
| Machinery Hours/km | ElasticNet |

Hyperparameter tuning was performed using **Optuna**.

---

### 📈 Interactive Dashboard

- Prediction summary
- Project comparison
- Feature importance
- Historical predictions
- Visualization charts

---

### 📂 Project History

Every prediction is automatically stored and can be revisited later.

---

### 📉 Visual Analytics

- Feature Importance
- Actual vs Predicted
- Residual Distribution
- Prediction History

---

## 🧠 Machine Learning Pipeline

```
Training Dataset
        │
        ▼
Data Cleaning
        │
        ▼
Feature Engineering
        │
        ▼
Model Selection
        │
        ▼
Hyperparameter Optimization (Optuna)
        │
        ▼
Final Model Training
        │
        ▼
Model Serialization
        │
        ▼
Prediction Dashboard
```

---

# 📊 Dataset

The training dataset contains over **3500 synthetic yet engineering-consistent road construction projects** generated using domain knowledge and realistic engineering constraints.

Each project contains:

- Road Geometry
- Pavement Design
- Earthwork Quantities
- Bridge Information
- Tunnel Information
- Traffic Characteristics
- Environmental Factors
- Material Prices
- Contractor Efficiency
- Equipment Information
- Labour Productivity
- Economic Indices

More than **80 engineering features** are used for prediction.

---

# 🛠️ Tech Stack

### Frontend

- Streamlit

### Backend

- Python

### Machine Learning

- Scikit-Learn
- CatBoost
- ElasticNet
- Optuna

### Data Processing

- Pandas
- NumPy

### Visualization

- Matplotlib
- Plotly

### Model Storage

- Joblib

---

# 📂 Project Structure

```
road-planning-platform/

│
├── app.py
├── requirements.txt
├── README.md
├── download_models.py
│
├── models/
│
├── assets/
│
├── src/
│   ├── pages/
│   ├── prediction/
│   ├── utils/
│   ├── visualization/
│   └── database/
│
├── data/
│
└── outputs/
```

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/Tavishi-Maini/road-planning-platform.git
```

Go inside the project

```bash
cd road-planning-platform
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment

### Windows

```bash
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the Application

```bash
streamlit run app.py
```

---

# 📈 Model Performance

| Target | R² Score |
|---------|----------|
| Total Cost | **0.9941** |
| Construction Duration | **0.9820** |
| Material Index | **0.9943** |
| Manpower Hours/km | **0.9537** |
| Machinery Hours/km | **0.9503** |

Hyperparameters were optimized using **Optuna**.

# 👩‍💻 Author

**Tavishi Maini**

B.Tech, Civil Engineering  
Indian Institute of Technology Kanpur

Interested in Machine Learning, Artificial Intelligence, Data Science, and Software Development.

