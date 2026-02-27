# Intelligent Device Health Monitoring System

This project monitors device health, detects anomalies, predicts failures, and displays insights using a Streamlit dashboard.

It follows a modular pipeline structure for data ingestion, transformation, health scoring, feature engineering, machine learning, and visualization.


## 📁 Project Structure

```
intelligent-device-health-monitoring-system/
│
├── data/               # Raw and processed datasets
│   ├── raw/            # Original CSVs (source of truth)
│   └── processed/      # Cleaned, merged, feature-engineered data
│
├── notebooks/          # Exploratory analysis
├── src/                # Core source code
│   ├── ingestion/      # Data loading modules
│   ├── transformation/ # Data merging & relational modeling
│   ├── health/         # Health scoring per device/interface
│   ├── features/       # Feature engineering for ML
│   ├── models/         # ML models & evaluation
│   ├── inference/      # Inference pipelines
│   └── utils/          # Utility functions (logging, helpers)
│
├── pipeline/           # Orchestration of full pipeline
│   └── run_pipeline.py
│
├── app/                # Streamlit dashboard application
│   └── device_health_app.py
├── main.py             # Entry point to run the full pipeline
├── config.yaml         # Configurations (paths, thresholds, hyperparameters)
└── requirements.txt    # Python dependencies
```

---

## 🚀 How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the pipeline

```bash
python main.py
```

### 3. Start the dashboard

```bash
python .\app\app.py
```

---

## 🔍 What It Does

* Loads and cleans relational device data
* Merges organization, asset, device, interface, and event data
* Calculates device and interface health scores
* Performs anomaly detection
* Predicts potential device failures
* Displays results in a Streamlit dashboard

---

## 🛠 Tech Stack

* Python
* Pandas
* Scikit-learn
* Streamlit
* Matplotlib / Seaborn

---

This project demonstrates an end-to-end machine learning pipeline for inventory device health monitoring 