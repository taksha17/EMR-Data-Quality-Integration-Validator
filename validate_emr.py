import pandas as pd
from emr_schema import EMRRecord
from typing import List
import os

def validate_emr_data(input_csv: str, output_dir: str):
    df = pd.read_csv(input_csv)
    valid_records = []
    invalid_records = []

    for _, row in df.iterrows():
        try:
            record = EMRRecord(**row.to_dict())
            valid_records.append(record.dict())
        except Exception as e:
            row["error"] = str(e)
            invalid_records.append(row)

    os.makedirs(output_dir, exist_ok=True)
    pd.DataFrame(valid_records).to_csv(f"{output_dir}/valid_emr.csv", index=False)
    pd.DataFrame(invalid_records).to_csv(f"{output_dir}/invalid_emr.csv", index=False)
    print(f"Validation complete! ✅ {len(valid_records)} valid, ❌ {len(invalid_records)} invalid.")

if __name__ == "__main__":
    validate_emr_data("sample_emr.csv", "validated_output")
