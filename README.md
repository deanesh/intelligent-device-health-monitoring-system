

`````markdown
# 🚀 Intelligent Device Health Monitoring

Monitor device health, detect anomalies, and visualize insights — fully **event-driven** and interactive.  

---

## 🗂 Folder Structure

````text
intelligent-device-health-monitoring-system/
│
├── app/                  # Streamlit/Dash dashboard + services
│   ├── app.py            # Dashboard main file
│   └── services/
│       └── device_health_app.py
│
├── data/
│   ├── raw/              # Original CSVs (source of truth)
│   └── processed/        # Cleaned / snapshot CSVs
│
├── notebooks/
│   └── exploratory_analysis.ipynb
│
├── pipeline/
│   └── run_pipeline.py
│
├── src/                  # Core modules
│   ├── transformation/   # Data merging & relational modeling
│   ├── health/           # Health scoring logic
│   ├── features/         # Feature engineering for ML
│   ├── models/           # ML models & evaluation
│   ├── inference/        # Inference pipelines
│   └── utils/            # Utility functions
│
├── main.py               # Pipeline entry point
├── config.yaml           # Configurations (paths, thresholds, hyperparameters)
└── requirements.txt      # Python dependencies
`````

---

## 🎯 Features

* Event-based **device health scoring**: Critical / Warning / Healthy
* Interactive **Dashboard** with 4 tabs:

  * **Overview** → KPIs + stacked health bar
  * **Country KPI** → Assets/Devices/Organizations by country
  * **Devices** → Device list + health status
  * **Events** → Event table & stats
* **EDA Notebook** (`exploratory_analysis.ipynb`) with top 10 countries, stored vs actual validations
* Modular pipeline: load → transform → health → dashboard

---

## ⚡ Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python main.py

# Explore data
jupyter notebook notebooks/exploratory_analysis.ipynb

# Launch dashboard
python app/app.py
```

---

## 📊 Health Scoring

* Start at **100** for all devices
* Deduct points per event type: `high_cpu`, `interface_down`, `critical_error`, etc.
* Categorize into **Critical / Warning / Healthy**
* Fully **event-driven**, no legacy health columns

---

## 🛠 Tech Stack

Python | Pandas | NumPy | Matplotlib | Seaborn | Plotly | Dash | Bootstrap

> 💡 Quick onboarding: run `main.py` → explore the **EDA notebook** → launch `app/app.py`


