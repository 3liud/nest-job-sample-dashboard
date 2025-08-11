# African Neonatal Outcomes Dashboard

This dashboard simulates a neonatal monitoring system aligned with the Minimal Neonatal Dataset (mND) structure. It showcases how key metrics and filters can support monitoring and evaluation (M&E) for neonatal care across hospitals and time.

Hosted version: [[Render URL](https://nest360-sample-neonatal-dashboard.onrender.com/)]

---

## Features

- Multi-select filters: Hospital, Outcome, Diagnosis, Year
- Interactive charts:
  - Outcomes by Diagnosis
  - Average Length of Stay
  - Monthly Admissions Trend
  - Birth Weight Distribution
  - Patient Outcome Proportions
- Summary cards:
  - Total Admissions
  - Number of Deaths
  - Average LOS
  - Average Birth Weight
- Sticky header and sidebar
- Dynamic chart titles based on filters

---

## Project Structure

```
├── app.py                  
├── data/
│   └── synthetic_mnd_data.csv
├── requirements.txt        
├── Procfile                
└── README.md
```

---

## Running the App Locally

### 1. Clone the repo

```bash
git clone https://github.com/3liud/nest-job-sample-dashboard.git
cd nest-job-sample-dashboard
```

### 2. Set up a virtual environment

**For macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**For Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

Then open [http://localhost:8050](http://localhost:8050) in your browser.

---

## Deploying on Render

### 1. Add these two files:

- `requirements.txt`  
- `Procfile`

### 2. Set `Procfile` content:

```bash
web: python app.py
```

### 3. Push your repo to GitHub, then connect it to [Render](https://render.com) and deploy as a **Web Service**.

Set:

- **Start command**: `python app.py`
- **Python version**: 3.x
- **Port binding**: Handled automatically via `os.environ.get("PORT")`

---

## Data

The app uses **synthetic neonatal data** based on the Minimal Neonatal Dataset (mND) for demonstration only. No real patient data is included.

---

## Author

Built by [Eliud](https://www.linkedin.com/in/3liud/), a data analyst passionate about applying data to improve health outcomes.

---
