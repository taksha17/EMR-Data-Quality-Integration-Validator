import pandas as pd
from emr_schema import EMRRecord
from typing import List
import os
from sklearn.ensemble import IsolationForest

def validate_emr_data(input_csv: str, output_dir: str):
    df = pd.read_csv(input_csv)
    
    # --- AI Anomaly Detection ---
    print("🤖 Starting AI anomaly detection...")

    # Identify the numeric columns to use for the model
    numeric_cols = ["heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic"]
    
    # Handle potential non-numeric data before feeding to the model
    df_numeric = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    df_numeric.fillna(df_numeric.mean(), inplace=True) # Fill NaNs for the model
    
    # Initialize and train the Isolation Forest model
    # The 'contamination' parameter is a hyperparameter you can tune based on your data.
    # It represents the expected proportion of outliers in the data.
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(df_numeric)
    
    # Predict anomalies. The result is -1 for anomalies and 1 for normal data.
    df['anomaly_prediction'] = model.predict(df_numeric)
    df['anomaly_score'] = model.decision_function(df_numeric)

    print("✅ AI detection complete. Adding anomaly status to records.")

    valid_records = []
    invalid_records = []

    for _, row in df.iterrows():
        try:
            # Set the anomaly status based on the prediction
            anomaly_status = "anomaly" if row["anomaly_prediction"] == -1 else "normal"
            
            # Use a Pydantic model to validate the record and pass the anomaly score
            record = EMRRecord(
                patient_id=row["patient_id"],
                name=row["name"],
                gender=row["gender"],
                dob=row["dob"],
                email=row["email"],
                diagnosis_code=row["diagnosis_code"],
                heart_rate=row["heart_rate"],
                blood_pressure_systolic=row["blood_pressure_systolic"],
                blood_pressure_diastolic=row["blood_pressure_diastolic"],
                anomaly_score=row["anomaly_score"],
                anomaly_status=anomaly_status
            )
            valid_records.append(record.dict())
        except Exception as e:
            row["error"] = str(e)
            invalid_records.append(row.to_dict())

    os.makedirs(output_dir, exist_ok=True)
    pd.DataFrame(valid_records).to_csv(f"{output_dir}/valid_emr.csv", index=False)
    pd.DataFrame(invalid_records).to_csv(f"{output_dir}/invalid_emr.csv", index=False)
    
    print(f"\nValidation complete! ✅ {len(valid_records)} valid, ❌ {len(invalid_records)} invalid.")
    print("Note: The valid records CSV now includes AI-generated anomaly scores and status.")


if __name__ == "__main__":
    validate_emr_data("sample_emr.csv", "validated_output")