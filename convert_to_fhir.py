# import pandas as pd
# import uuid
# import json
# from datetime import date # Standard Python date object
# from fhir.resources.patient import Patient
# from fhir.resources.observation import Observation
# from fhir.resources.humanname import HumanName
# from fhir.resources.condition import Condition
# from fhir.resources.reference import Reference
# from fhir.resources.codeableconcept import CodeableConcept
# from fhir.resources.coding import Coding
# from fhir.resources.bundle import Bundle, BundleEntry

# import pandas as pd
# import uuid
# import json
# from datetime import date
# from fhir.resources.patient import Patient
# from fhir.resources.observation import Observation
# from fhir.resources.humanname import HumanName
# from fhir.resources.condition import Condition
# from fhir.resources.reference import Reference
# from fhir.resources.codeableconcept import CodeableConcept
# from fhir.resources.coding import Coding
# from fhir.resources.bundle import Bundle, BundleEntry

# def convert_emr_to_fhir(sample_emr_csv: str, output_json: str):
#     df = pd.read_csv(sample_emr_csv)
#     entries = []

#     for _, row in df.iterrows():
#         patient_id = row["patient_id"]

#         # --- Patient Resource ---
#         patient = Patient(
#             id=patient_id,
#             gender=row["gender"].lower(),
#             birthDate=row["dob"],
#             name=[HumanName(text=row["name"])],
#             telecom=[{"system": "email", "value": row["email"], "use": "home"}]
#         )
#         entries.append(BundleEntry(resource=patient))

#         # --- Condition Resource ---
#         # FIX: Added the required 'clinicalStatus' field.
#         condition = Condition(
#             subject=Reference(reference=f"Patient/{patient_id}"),
#             code=CodeableConcept(
#                 coding=[Coding(system="http://hl7.org/fhir/sid/icd-10", code=row["diagnosis_code"])]
#             ),
#             clinicalStatus=CodeableConcept(
#                 coding=[
#                     Coding(
#                         system="http://terminology.hl7.org/CodeSystem/condition-clinical",
#                         code="active"
#                     )
#                 ]
#             )
#         )
#         entries.append(BundleEntry(resource=condition))

#         # --- Observation Time ---
#         observation_time = date(2024, 1, 1)

#         # --- Observation: Heart Rate ---
#         heart_rate = Observation(
#             status="final",
#             effectiveDateTime=observation_time,
#             code=CodeableConcept(
#                 coding=[Coding(system="http://loinc.org", code="8867-4", display="Heart rate")]
#             ),
#             subject=Reference(reference=f"Patient/{patient_id}"),
#             valueQuantity={"value": row["heart_rate"], "unit": "beats/minute"},
#         )
#         entries.append(BundleEntry(resource=heart_rate))

#         # --- Observation: Blood Pressure ---
#         bp = Observation(
#             status="final",
#             effectiveDateTime=observation_time,
#             code=CodeableConcept(
#                 coding=[Coding(system="http://loinc.org", code="85354-9", display="Blood pressure panel")]
#             ),
#             component=[
#                 {
#                     "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic"}]},
#                     "valueQuantity": {"value": row["blood_pressure_systolic"], "unit": "mmHg"}
#                 },
#                 {
#                     "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic"}]},
#                     "valueQuantity": {"value": row["blood_pressure_diastolic"], "unit": "mmHg"}
#                 }
#             ],
#             subject=Reference(reference=f"Patient/{patient_id}")
#         )
#         entries.append(BundleEntry(resource=bp))

#     # --- Final Bundle ---
#     fhir_bundle = Bundle(
#         type="collection",
#         entry=entries
#     )

#     with open(output_json, "w") as f:
#         f.write(fhir_bundle.json(indent=2))

#     print(f"✅ Converted to FHIR format: {output_json}")


# if __name__ == "__main__":
#     convert_emr_to_fhir("sample_emr.csv", "output_fhir.json")

import pandas as pd
import uuid
import json
from datetime import date
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.humanname import HumanName
from fhir.resources.condition import Condition
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.bundle import Bundle, BundleEntry
import os

def convert_emr_to_fhir(input_csv: str, output_json: str):
    # Ensure the input CSV exists
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        print("Please run validate_emr.py first to create the validated output.")
        return

    df = pd.read_csv(input_csv)
    entries = []

    for _, row in df.iterrows():
        patient_id = row["patient_id"]

        # --- Patient Resource ---
        patient = Patient(
            id=patient_id,
            gender=row["gender"].lower(),
            birthDate=row["dob"],
            name=[HumanName(text=row["name"])],
            telecom=[{"system": "email", "value": row["email"], "use": "home"}]
        )
        entries.append(BundleEntry(resource=patient))

        # --- Condition Resource ---
        condition = Condition(
            subject=Reference(reference=f"Patient/{patient_id}"),
            code=CodeableConcept(
                coding=[Coding(system="http://hl7.org/fhir/sid/icd-10", code=row["diagnosis_code"])]
            ),
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                        code="active"
                    )
                ]
            )
        )
        entries.append(BundleEntry(resource=condition))

        # --- Observation Time ---
        observation_time = date(2024, 1, 1)

        # --- Observation: Heart Rate ---
        heart_rate = Observation(
            status="final",
            effectiveDateTime=observation_time,
            code=CodeableConcept(
                coding=[Coding(system="http://loinc.org", code="8867-4", display="Heart rate")]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            valueQuantity={"value": row["heart_rate"], "unit": "beats/minute"},
        )
        entries.append(BundleEntry(resource=heart_rate))

        # --- Observation: Blood Pressure ---
        bp = Observation(
            status="final",
            effectiveDateTime=observation_time,
            code=CodeableConcept(
                coding=[Coding(system="http://loinc.org", code="85354-9", display="Blood pressure panel")]
            ),
            component=[
                {
                    "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6", "display": "Systolic"}]},
                    "valueQuantity": {"value": row["blood_pressure_systolic"], "unit": "mmHg"}
                },
                {
                    "code": {"coding": [{"system": "http://loinc.org", "code": "8462-4", "display": "Diastolic"}]},
                    "valueQuantity": {"value": row["blood_pressure_diastolic"], "unit": "mmHg"}
                }
            ],
            subject=Reference(reference=f"Patient/{patient_id}")
        )
        entries.append(BundleEntry(resource=bp))

        # --- NEW: Observation for AI Anomaly Score and Status ---
        anomaly_obs = Observation(
            status="final",
            effectiveDateTime=observation_time,
            code=CodeableConcept(
                # Using a custom code for the AI anomaly observation
                coding=[Coding(
                    system="https://example.org/fhir/ai-validator-codes", 
                    code="ai-anomaly-status", 
                    display="AI Anomaly Status"
                )]
            ),
            subject=Reference(reference=f"Patient/{patient_id}"),
            valueString=str(row["anomaly_status"]),
            # You can also add the score as a valueQuantity if needed
            # For simplicity, we are just storing the status in this example
        )
        entries.append(BundleEntry(resource=anomaly_obs))

    # --- Final Bundle ---
    fhir_bundle = Bundle(
        type="collection",
        entry=entries
    )

    with open(output_json, "w") as f:
        f.write(fhir_bundle.json(indent=2))

    print(f"✅ Converted to FHIR format: {output_json}")


if __name__ == "__main__":
    convert_emr_to_fhir("validated_output/valid_emr.csv", "output_fhir.json")