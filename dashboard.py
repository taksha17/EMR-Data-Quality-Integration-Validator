import streamlit as st
import json
import pandas as pd 

# --- Helper Function to get resources for a patient ---
def get_patient_resources(resources, patient_id):
    patient_resources = {
        "patient": None,
        "conditions": [],
        "llm_diagnoses": [],
        "observations": [],
        "ai_anomaly": None
    }
    
    for res in resources:
        res_type = res.get('resourceType')
        
        if res_type == 'Patient' and res.get('id') == patient_id:
            patient_resources["patient"] = res
        elif res.get('subject', {}).get('reference') == f"Patient/{patient_id}":
            if res_type == 'Condition':
                coding_system = res.get('code', {}).get('coding', [{}])[0].get('system')
                if coding_system == "https://example.org/fhir/llm-diagnoses":
                    patient_resources["llm_diagnoses"].append(res)
                else:
                    patient_resources["conditions"].append(res)
            elif res_type == 'Observation':
                if res.get('code', {}).get('coding', [{}])[0].get('code') == 'ai-anomaly-status':
                    patient_resources["ai_anomaly"] = res
                else:
                    patient_resources["observations"].append(res)
                    
    return patient_resources


# --- Dashboard Script ---
st.set_page_config(layout="wide") # Use wide layout for a better dashboard experience

# Loading FHIR-converted JSON
with open("output_fhir.json") as f:
    fhir_bundle = json.load(f)

try:
    resources = [entry['resource'] for entry in fhir_bundle.get('entry', [])]
except (TypeError, KeyError):
    st.error("The loaded JSON is not in the expected FHIR Bundle format. Please ensure 'convert_to_fhir.py' was run correctly.")
    resources = []


# --- Main Dashboard Title ---
st.title("FHIR Patient Dashboard")
st.markdown("A unified view of patient records with AI and LLM insights.")

# --- UI Controls and Filters ---
patients = [res for res in resources if res['resourceType'] == 'Patient']

# Creating a DataFrame for easier filtering
patient_df = pd.DataFrame([{'id': p['id'], 'name': p['name'][0]['text']} for p in patients])

# Getting anomaly status for each patient
all_patient_resources = {p['id']: get_patient_resources(resources, p['id']) for p in patients}
anomaly_counts = sum(1 for data in all_patient_resources.values() if data["ai_anomaly"] and data["ai_anomaly"]["valueString"] == 'anomaly')

# Let's display summary metrics at the top
st.subheader("Summary Statistics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Patients", len(patients))
with col2:
    st.metric("Patients with Anomalies", anomaly_counts, delta_color="inverse")
with col3:
    st.metric("LLM Diagnoses Found", sum(1 for data in all_patient_resources.values() if data["llm_diagnoses"]))

st.markdown("---")

# Filtering Sections
st.subheader("Filter Patient Records")
search_query = st.text_input("Search by Patient Name or ID", "")
anomaly_filter = st.selectbox("Filter by AI Anomaly Status", ["All", "anomaly", "normal"])

# Filtering logic
filtered_patients = []
for p in patients:
    patient_id = p.get('id', '')
    name = p.get('name', [{}])[0].get('text', '')
    
    # Check search query
    search_match = search_query.lower() in name.lower() or search_query.lower() in patient_id.lower()
    if not search_match:
        continue
    
    # Check anomaly filter
    anomaly_status = all_patient_resources[patient_id]["ai_anomaly"]["valueString"] if all_patient_resources[patient_id]["ai_anomaly"] else None
    if anomaly_filter != "All" and anomaly_status != anomaly_filter:
        continue

    filtered_patients.append(p)

if not filtered_patients:
    st.info("No patients match the current filters.")

# --- Displaying Filtered Patient Records ---
st.subheader(f"Displaying {len(filtered_patients)} of {len(patients)} Patients")

if filtered_patients:
    for p in filtered_patients:
        p_id = p.get('id', '')
        patient_data = all_patient_resources[p_id]
        
        name = p.get("name", [{}])[0].get("text", "Unknown")
        gender = p.get("gender", "N/A")
        birth_date = p.get("birthDate", "N/A")
        
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
                email = p.get("telecom", [{}])[0].get("value", "N/A")
                st.markdown(f"**Email**: {email}")
            
            st.markdown("---")
            
            # --- Vitals (Observations) ---
            st.markdown("**Vitals**")
            vitals_cols = st.columns(3)
            
            heart_rate_obs = next((obs for obs in patient_data["observations"] if obs['code']['coding'][0]['code'] == '8867-4'), None)
            if heart_rate_obs:
                hr_value = heart_rate_obs['valueQuantity']['value']
                hr_unit = heart_rate_obs['valueQuantity']['unit']
                with vitals_cols[0]:
                    st.metric("Heart Rate", f"{hr_value} {hr_unit}")
            
            bp_obs = next((obs for obs in patient_data["observations"] if obs['code']['coding'][0]['code'] == '85354-9'), None)
            if bp_obs:
                systolic = bp_obs['component'][0]['valueQuantity']['value']
                diastolic = bp_obs['component'][1]['valueQuantity']['value']
                with vitals_cols[1]:
                    st.metric("Blood Pressure", f"{systolic}/{diastolic} mmHg")
                    
            st.markdown("---")
            
            # --- Conditions ---
            st.markdown("**Conditions**")

            if patient_data["llm_diagnoses"]:
                for condition in patient_data["llm_diagnoses"]:
                    diagnosis = condition.get('code', {}).get('coding', [{}])[0].get('display', 'N/A')
                    st.markdown(f"🧠 **LLM Diagnosis**: `{diagnosis}`")

            if patient_data["conditions"]:
                for condition in patient_data["conditions"]:
                    diagnosis = condition.get('code', {}).get('coding', [{}])[0].get('display', 'N/A')
                    st.markdown(f"📝 **CSV Diagnosis**: `{diagnosis}`")
            
            st.markdown("---")