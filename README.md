# EMR-Data-Quality-Integration-Validator

Project Description

This project is an end-to-end solution for validating and integrating Electronic Medical Record (EMR) data. It demonstrates a modern data pipeline that uses Python to simulate EMR data, apply both traditional and AI-powered data quality checks, convert the data into the FHIR (Fast Healthcare Interoperability Resources) standard, and visualize the results in an interactive dashboard.

The project highlights the use of advanced techniques, including:

  - AI for Anomaly Detection: Identifying subtle data errors and outliers.
  - LLMs for Unstructured Data: Extracting structured information (e.g., diagnoses) from free-text doctor's notes.
  - FHIR Conversion: Standardizing data for interoperability with other health systems.
  - Interactive Dashboard: A Streamlit-based interface for visualizing patient records and AI insights.



Features

  Synthetic Data Generation: Creates realistic EMR data in a CSV format using the `Faker` library.
  Data Validation: Validates data types and ranges using a Pydantic model.
  AI Anomaly Detection: Employs an Isolation Forest model to flag unusual patient records.
  LLM-Powered Extraction: Uses a Large Language Model to parse doctor's notes and extract diagnoses.
  FHIR Conversion: Transforms the validated and enhanced data into a FHIR Bundle JSON format.
  Interactive Dashboard: A Streamlit application for searching, filtering, and viewing patient data, including LLM and AI insights.



Prerequisites

Before you begin, ensure you have the following installed:

  * Python 3.8+
  * `pip` (Python's package installer)
  * An OpenAI API Key (required for LLM functionality)



Installation

1.  Clone the repository:
    git clone https://github.com/your-username/EMR-Data-Quality-Integration-Validator.git
    cd EMR-Data-Quality-Integration-Validator
   

2.  Create and activate a virtual environment:
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    venv\Scripts\activate   # On Windows
    

3.  Install the dependencies:
    The project uses a `requirements.txt` file to manage its dependencies.
    pip install -r requirements.txt
    

4.  Set your OpenAI API Key:
    The project uses the `OPENAI_API_KEY` environment variable for authentication.

    On macOS/Linux:
    export OPENAI_API_KEY="your_api_key_here"

    On Windows:
    set OPENAI_API_KEY="your_api_key_here"
    

    *(Replace `"your_api_key_here"` with your actual key.)*

Usage

Run the project by executing the scripts in the following order:

1.  Generate Fake EMR Data:
    python generate_fake_data.py
    This creates `sample_emr.csv` with structured and unstructured data.

2.  Validate Data with AI Anomaly Detection:
    python validate_emr.py
    This script performs validation and generates `validated_output/valid_emr.csv`.

3.  Convert Data to FHIR with LLM Insights:
    python convert_to_fhir.py
    This processes the data and creates a FHIR bundle in `output_fhir.json`.

4.  Run the Interactive Dashboard:
    streamlit run dashboard.py
    This will open the dashboard in your web browser.



File Structure

EMR-Data-Quality-Integration-Validator/
├── generate_fake_data.py
├── validate_emr.py
├── convert_to_fhir.py
├── dashboard.py
├── emr_schema.py
├── output_fhir.json         # FHIR output (generated)
├── sample_emr.csv           # Raw data (generated)
├── validated_output/
│   ├── valid_emr.csv        # Validated data (generated)
│   └── invalid_emr.csv      # Invalid data (generated)
└── README.md

Dependencies (`requirements.txt`)
Create a `requirements.txt` file with the following content:

pandas
faker
pydantic>=2.7.4
fhir.resources
streamlit
scikit-learn
langchain
langchain-openai
openai