import pandas as pd
import numpy as np
import random
from datetime import timedelta, datetime

np.random.seed(42)

n = 15000

def random_date(start, end):
    return start + timedelta(days=random.randint(0, int((end - start).days)))

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 1, 1)

data = pd.DataFrame({
    'Patient_ID': [f'PID{1000+i}' for i in range(n)],
    'Admission_Date': [random_date(start_date, end_date) for _ in range(n)],
    'Birth_Weight_g': np.random.normal(2500, 500, n).astype(int),
    'Gestational_Age_weeks': np.random.normal(36, 3, n).astype(int),
    'Diagnosis': np.random.choice(['Sepsis', 'Asphyxia', 'Preterm', 'Jaundice', 'RDS'], n),
    'Treatment': np.random.choice(['Antibiotics', 'Oxygen', 'CPAP', 'Phototherapy', 'None'], n),
    'Outcome': np.random.choice(['Recovered', 'Referred', 'Died'], n, p=[0.75, 0.15, 0.10]),
    'Sex': np.random.choice(['Male', 'Female'], n),
    'Hospital': np.random.choice(['Facility A', 'Facility B', 'Facility C', 'Home'], n)
})

# Calculate discharge date as admission date + random 2–14 days
data['Discharge_Date'] = data['Admission_Date'] + pd.to_timedelta(np.random.randint(2, 15, n), unit='d')
data['Length_of_Stay_days'] = (data['Discharge_Date'] - data['Admission_Date']).dt.days

data.to_csv("data/synthetic_mnd_data.csv", index=False)
