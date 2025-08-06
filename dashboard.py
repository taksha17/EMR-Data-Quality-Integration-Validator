import streamlit as st
import pandas as pd
import json

# Load FHIR-converted JSON
with open("output_fhir.json") as f:
    fhir_bundle = json.load(f)

# The FHIR Bundle contains resources in the 'entry' list.
# We need to access the 'resource' key for each entry.
try:
    resources = [entry['resource'] for entry in fhir_bundle.get('entry', [])]
except (TypeError, KeyError):
    st.error("The loaded JSON is not in the expected FHIR Bundle format. Please ensure 'convert_to_fhir.py' was run correctly.")
    resources = []


# Filter and display Patient Data
patients = [res for res in resources if res['resourceType'] == 'Patient']
st.title("FHIR Patient Dashboard")
st.subheader("Patient Overview")
for patient in patients:
    # Safely access nested dictionary values using .get()
    name = patient.get("name", [{}])[0].get("text", "Unknown")
    gender = patient.get("gender", "N/A")
    birth_date = patient.get("birthDate", "N/A")
    email = patient.get("telecom", [{}])[0].get("value", "N/A")
    
    st.markdown(f"**Name**: {name}  \n**Gender**: {gender}  \n**DOB**: {birth_date}  \n**Email**: {email}")
    st.markdown("---")


# Filter and display Conditions
conditions = [res for res in resources if res['resourceType'] == 'Condition']
st.subheader("Patient Conditions")
for condition in conditions:
    patient_id = condition.get("subject", {}).get("reference", "N/A").replace("Patient/", "")
    diagnosis = condition.get("code", {}).get("coding", [{}])[0].get("display", "N/A")
    st.markdown(f"**Patient ID**: {patient_id}  \n**Diagnosis**: {diagnosis}")
    st.markdown("---")


# Filter and display Observations
observations = [res for res in resources if res['resourceType'] == 'Observation']
st.subheader("Patient Observations")
for observation in observations:
    patient_id = observation.get("subject", {}).get("reference", "N/A").replace("Patient/", "")
    
    # Check the observation type and display accordingly
    code_display = observation.get("code", {}).get("coding", [{}])[0].get("display", "N/A")
    
    if code_display == 'Blood pressure panel':
        systolic = observation.get("component", [{}])[0].get("valueQuantity", {}).get("value", "N/A")
        diastolic = observation.get("component", [{}])[1].get("valueQuantity", {}).get("value", "N/A")
        st.markdown(f"**Patient ID**: {patient_id}  \n**Blood Pressure**: {systolic}/{diastolic} mmHg")
    elif code_display == 'Heart rate':
        heart_rate = observation.get("valueQuantity", {}).get("value", "N/A")
        unit = observation.get("valueQuantity", {}).get("unit", "N/A")
        st.markdown(f"**Patient ID**: {patient_id}  \n**Heart Rate**: {heart_rate} {unit}")
    
    st.markdown("---")