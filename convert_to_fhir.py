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

# --- Importing Langchain/OpenAI API's ---
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser

# Initializing the LLM (using OpenAI's gpt-3.5-turbo for demo purpose)
# Here we need to make sure we have our OPENAI_API_KEY set as an environment variable
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# Creating a prompt template for our task
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a medical assistant that extracts information from clinical notes."),
    ("user", "Extract a single primary diagnosis from the following note and return only the diagnosis name, not the code or any other text. If no diagnosis is found, return 'No Diagnosis Found'. The note is: {notes}"),
])

# Creating a simple chain
chain = prompt_template | llm | StrOutputParser()

def convert_emr_to_fhir(input_csv: str, output_json: str):
    # This script now reads the CSV with the notes column
    df = pd.read_csv(input_csv)
    entries = []

    for _, row in df.iterrows():
        patient_id = row["patient_id"]
        
        # --- LLM Processing of Notes ---
        notes_text = row.get("notes")
        llm_diagnosis_name = "No Diagnosis Found"
        if notes_text and notes_text != "No Diagnosis Found":
            try:
                # Use the LLM chain to get the diagnosis from the notes
                llm_diagnosis_name = chain.invoke({"notes": notes_text})
                # Clean up the output (remove extra quotes, etc.)
                llm_diagnosis_name = llm_diagnosis_name.strip('\"')
            except Exception as e:
                print(f"Error invoking LLM for patient {patient_id}: {e}")
                llm_diagnosis_name = "LLM Extraction Failed"

        # --- Patient Resource ---
        patient = Patient(
            id=patient_id,
            gender=row["gender"].lower(),
            birthDate=row["dob"],
            name=[HumanName(text=row["name"])],
            telecom=[{"system": "email", "value": row["email"], "use": "home"}]
        )
        entries.append(BundleEntry(resource=patient))

        # --- LLM-Extracted Condition Resource ---
        if llm_diagnosis_name != "No Diagnosis Found" and llm_diagnosis_name != "LLM Extraction Failed":
            llm_condition = Condition(
                subject=Reference(reference=f"Patient/{patient_id}"),
                code=CodeableConcept(
                    coding=[Coding(
                        system="https://example.org/fhir/llm-diagnoses",
                        code=llm_diagnosis_name.replace(" ", "_").lower(),
                        display=llm_diagnosis_name
                    )]
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
            entries.append(BundleEntry(resource=llm_condition))
        
        # --- Observation: Heart Rate ---
        heart_rate = Observation(
            status="final",
            effectiveDateTime=date(2024, 1, 1),
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
            effectiveDateTime=date(2024, 1, 1),
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

    # --- Final Bundle ---
    fhir_bundle = Bundle(
        type="collection",
        entry=entries
    )

    with open(output_json, "w") as f:
        f.write(fhir_bundle.json(indent=2))

    print(f"✅ Converted to FHIR format with LLM insights: {output_json}")


if __name__ == "__main__":
    # Note: This script now reads the standard sample_emr.csv
    convert_emr_to_fhir("sample_emr.csv", "output_fhir.json")