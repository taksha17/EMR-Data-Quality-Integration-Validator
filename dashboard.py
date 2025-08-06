# import streamlit as st
# import pandas as pd
# import json

# # Load FHIR-converted JSON
# with open("output_fhir.json") as f:
#     fhir_bundle = json.load(f)

# # The FHIR Bundle contains resources in the 'entry' list.
# # We need to access the 'resource' key for each entry.
# try:
#     resources = [entry['resource'] for entry in fhir_bundle.get('entry', [])]
# except (TypeError, KeyError):
#     st.error("The loaded JSON is not in the expected FHIR Bundle format. Please ensure 'convert_to_fhir.py' was run correctly.")
#     resources = []


# # Filter and display Patient Data
# patients = [res for res in resources if res['resourceType'] == 'Patient']
# st.title("FHIR Patient Dashboard")
# st.subheader("Patient Overview")
# for patient in patients:
#     # Safely access nested dictionary values using .get()
#     name = patient.get("name", [{}])[0].get("text", "Unknown")
#     gender = patient.get("gender", "N/A")
#     birth_date = patient.get("birthDate", "N/A")
#     email = patient.get("telecom", [{}])[0].get("value", "N/A")
    
#     st.markdown(f"**Name**: {name}  \n**Gender**: {gender}  \n**DOB**: {birth_date}  \n**Email**: {email}")
#     st.markdown("---")


# # Filter and display Conditions
# conditions = [res for res in resources if res['resourceType'] == 'Condition']
# st.subheader("Patient Conditions")
# for condition in conditions:
#     patient_id = condition.get("subject", {}).get("reference", "N/A").replace("Patient/", "")
#     diagnosis = condition.get("code", {}).get("coding", [{}])[0].get("display", "N/A")
#     st.markdown(f"**Patient ID**: {patient_id}  \n**Diagnosis**: {diagnosis}")
#     st.markdown("---")


# # Filter and display Observations
# observations = [res for res in resources if res['resourceType'] == 'Observation']
# st.subheader("Patient Observations")
# for observation in observations:
#     patient_id = observation.get("subject", {}).get("reference", "N/A").replace("Patient/", "")
    
#     # Check the observation type and display accordingly
#     code_display = observation.get("code", {}).get("coding", [{}])[0].get("display", "N/A")
    
#     if code_display == 'Blood pressure panel':
#         systolic = observation.get("component", [{}])[0].get("valueQuantity", {}).get("value", "N/A")
#         diastolic = observation.get("component", [{}])[1].get("valueQuantity", {}).get("value", "N/A")
#         st.markdown(f"**Patient ID**: {patient_id}  \n**Blood Pressure**: {systolic}/{diastolic} mmHg")
#     elif code_display == 'Heart rate':
#         heart_rate = observation.get("valueQuantity", {}).get("value", "N/A")
#         unit = observation.get("valueQuantity", {}).get("unit", "N/A")
#         st.markdown(f"**Patient ID**: {patient_id}  \n**Heart Rate**: {heart_rate} {unit}")
    
#     st.markdown("---")

import streamlit as st
import json

# --- Helper Function to get resources for a patient ---
def get_patient_resources(resources, patient_id):
    patient_resources = {
        "patient": None,
        "conditions": [],
        "observations": [],
        "ai_anomaly": None
    }
    
    for res in resources:
        res_type = res.get('resourceType')
        
        # Check if the resource belongs to the current patient
        if res_type == 'Patient' and res.get('id') == patient_id:
            patient_resources["patient"] = res
        elif res.get('subject', {}).get('reference') == f"Patient/{patient_id}":
            if res_type == 'Condition':
                patient_resources["conditions"].append(res)
            elif res_type == 'Observation':
                # Check for the specific AI anomaly observation
                if res.get('code', {}).get('coding', [{}])[0].get('code') == 'ai-anomaly-status':
                    patient_resources["ai_anomaly"] = res
                else:
                    patient_resources["observations"].append(res)
                    
    return patient_resources


# --- Dashboard Script ---
# Load FHIR-converted JSON
with open("output_fhir.json") as f:
    fhir_bundle = json.load(f)

# The FHIR Bundle contains resources in the 'entry' list.
try:
    resources = [entry['resource'] for entry in fhir_bundle.get('entry', [])]
except (TypeError, KeyError):
    st.error("The loaded JSON is not in the expected FHIR Bundle format. Please ensure 'convert_to_fhir.py' was run correctly.")
    resources = []


# --- Main Dashboard Title ---
st.title("FHIR Patient Dashboard")
st.subheader("Unified Patient Records with AI Insights")

# Get a unique list of patient IDs from the resources
patient_ids = [res['id'] for res in resources if res['resourceType'] == 'Patient']

if patient_ids:
    for p_id in patient_ids:
        patient_data = get_patient_resources(resources, p_id)
        
        patient = patient_data["patient"]
        
        # Get Patient Demographics
        name = patient.get("name", [{}])[0].get("text", "Unknown")
        gender = patient.get("gender", "N/A")
        birth_date = patient.get("birthDate", "N/A")
        
        # Create a collapsible expander for each patient
        with st.expander(f"**Patient ID: {p_id}** - {name}", expanded=True):
            
            # --- AI Anomaly Status ---
            anomaly_obs = patient_data["ai_anomaly"]
            if anomaly_obs:
                status = anomaly_obs.get('valueString', 'N/A')
                if status == 'anomaly':
                    st.error("🚨 **AI Anomaly Detected**", icon="🚨")
                else:
                    st.success("✔️ **AI Status**: Normal", icon="✔️")
            
            st.markdown("---")
            
            # --- Demographics and Contact ---
            st.markdown("**Demographics**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Name**: {name}")
                st.markdown(f"**ID**: {p_id}")
            with col2:
                st.markdown(f"**Gender**: {gender}")
                st.markdown(f"**DOB**: {birth_date}")
            with col3:
                email = patient.get("telecom", [{}])[0].get("value", "N/A")
                st.markdown(f"**Email**: {email}")
            
            st.markdown("---")
            
            # --- Vitals (Observations) ---
            st.markdown("**Vitals**")
            vitals_cols = st.columns(3)
            
            # Display Heart Rate
            heart_rate_obs = next((obs for obs in patient_data["observations"] if obs['code']['coding'][0]['code'] == '8867-4'), None)
            if heart_rate_obs:
                hr_value = heart_rate_obs['valueQuantity']['value']
                hr_unit = heart_rate_obs['valueQuantity']['unit']
                with vitals_cols[0]:
                    st.metric("Heart Rate", f"{hr_value} {hr_unit}")
            
            # Display Blood Pressure
            bp_obs = next((obs for obs in patient_data["observations"] if obs['code']['coding'][0]['code'] == '85354-9'), None)
            if bp_obs:
                systolic = bp_obs['component'][0]['valueQuantity']['value']
                diastolic = bp_obs['component'][1]['valueQuantity']['value']
                with vitals_cols[1]:
                    st.metric("Blood Pressure", f"{systolic}/{diastolic} mmHg")
                    
            st.markdown("---")
            
            # --- Conditions ---
            st.markdown("**Conditions**")
            for condition in patient_data["conditions"]:
                diagnosis = condition.get('code', {}).get('coding', [{}])[0].get('display', 'N/A')
                st.markdown(f"**Diagnosis**: {diagnosis}")
            
            st.markdown("---")