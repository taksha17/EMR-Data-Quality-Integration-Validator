from faker import Faker
import pandas as pd
import random

fake = Faker()

def generate_emr_data(n=100):
    records = []
    for _ in range(n):
        record = {
            "patient_id": fake.uuid4(),
            "name": fake.name(),
            "dob": fake.date_of_birth(minimum_age=0, maximum_age=90).isoformat(),
            "gender": random.choice(["Male", "Female", "Other"]),
            "email": fake.email(),
            "diagnosis_code": random.choice(["I10", "E11", "J45", "K21", "N18"]),
            "heart_rate": random.randint(50, 120),
            "blood_pressure_systolic": random.randint(90, 180),
            "blood_pressure_diastolic": random.randint(60, 100),
        }
        records.append(record)
    return pd.DataFrame(records)

if __name__ == "__main__":
    df = generate_emr_data(100)
    df.to_csv("sample_emr.csv", index=False)
